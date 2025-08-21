
import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.db_service import database, connect_db, disconnect_db, create_tables
from services.db_service.models import Contact
from datetime import datetime
from services.authservice import AuthService, UserSignup, UserLogin, TokenResponse, User
from pydantic import BaseModel

# Database lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_db()
    create_tables()
    yield
    # Shutdown
    await disconnect_db()

app = FastAPI(lifespan=lifespan)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Mount static files for uploaded photos
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Security
security = HTTPBearer()

# Pydantic models for request/response
class ContactCreate(BaseModel):
    name: str
    email: Optional[str] = None

class ContactResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: str
    updated_at: str

# Initialize AuthService with database
def get_auth_service():
    return AuthService(database)

# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    token = credentials.credentials
    return await auth_service.get_current_user(token)

# File upload helper
async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return filename"""
    if not upload_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join("uploads", filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await upload_file.read()
        buffer.write(content)
    
    return filename

# Authentication endpoints
@app.post("/auth/signup", response_model=TokenResponse)
async def signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    photo: Optional[UploadFile] = File(None),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    user_data = UserSignup(username=username, email=email, password=password)
    
    photo_filename = None
    if photo:
        photo_filename = await save_upload_file(photo)
    
    return await auth_service.signup(user_data, photo_filename)

@app.post("/auth/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user"""
    return await auth_service.login(login_data)

@app.post("/auth/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user"""
    token = credentials.credentials
    return await auth_service.logout(token)

@app.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str = Form(...),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    return await auth_service.refresh_access_token(refresh_token)

# Contacts endpoints (now with real database data)
@app.get("/persons")
async def read_contacts(current_user: User = Depends(get_current_user)):
    """Get all contacts for the current user from crm_contacts table (with new simplified fields)"""
    try:
        query = """
        SELECT id, user_id, name, email, created_at, updated_at, is_favorite, last_accessed_at
        FROM crm_contacts 
        WHERE user_id = :user_id 
        ORDER BY name ASC
        """
        contacts = await database.fetch_all(query, {"user_id": current_user.id})
        return [
            {
                "id": str(contact["id"]),
                "name": contact["name"],
                "email": contact["email"] or "",
                "created_at": contact["created_at"],
                "updated_at": contact["updated_at"],
                "is_favorite": contact["is_favorite"],
                "last_accessed_at": contact["last_accessed_at"].isoformat() if contact["last_accessed_at"] else None
            }
            for contact in contacts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/persons/{person_id}")
async def read_contact(person_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific contact by ID for the current user (with new simplified fields)"""
    try:
        query = """
        SELECT id, user_id, name, email, created_at, updated_at, is_favorite, last_accessed_at
        FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        """
        contact = await database.fetch_one(query, {
            "contact_id": person_id,
            "user_id": current_user.id
        })
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {
            "id": str(contact["id"]),
            "name": contact["name"],
            "email": contact["email"] or "",
            "created_at": contact["created_at"],
            "updated_at": contact["updated_at"],
            "is_favorite": contact["is_favorite"],
            "last_accessed_at": contact["last_accessed_at"].isoformat() if contact["last_accessed_at"] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/persons", response_model=ContactResponse)
async def create_contact(
    contact_data: ContactCreate, 
    current_user: User = Depends(get_current_user)
):
    """Create a new contact for the current user"""
    try:
        # Generate UUID for the new contact
        contact_id = str(uuid.uuid4())
        
        query = """
        INSERT INTO crm_contacts (id, user_id, name, email, created_at, updated_at) 
        VALUES (:id, :user_id, :name, :email, NOW(), NOW())
        RETURNING id, user_id, name, email, created_at, updated_at
        """
        
        result = await database.fetch_one(query, {
            "id": contact_id,
            "user_id": current_user.id,
            "name": contact_data.name,
            "email": contact_data.email
        })
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create contact")
        
        return ContactResponse(
            id=str(result["id"]),
            name=result["name"],
            email=result["email"] or "",
            created_at=result["created_at"].isoformat(),
            updated_at=result["updated_at"].isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/persons/{person_id}", response_model=ContactResponse)
async def update_contact(
    person_id: str,
    contact_data: ContactCreate,
    current_user: User = Depends(get_current_user)
):
    """Update a contact for the current user"""
    try:
        # First check if the contact exists and belongs to the user
        check_query = """
        SELECT id FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        """
        existing_contact = await database.fetch_one(check_query, {
            "contact_id": person_id,
            "user_id": current_user.id
        })
        
        if not existing_contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Update the contact
        update_query = """
        UPDATE crm_contacts 
        SET name = :name, email = :email, updated_at = NOW() 
        WHERE id = :contact_id AND user_id = :user_id
        RETURNING id, user_id, name, email, created_at, updated_at
        """
        
        result = await database.fetch_one(update_query, {
            "contact_id": person_id,
            "user_id": current_user.id,
            "name": contact_data.name,
            "email": contact_data.email
        })
        
        return ContactResponse(
            id=str(result["id"]),
            name=result["name"],
            email=result["email"] or "",
            created_at=result["created_at"].isoformat(),
            updated_at=result["updated_at"].isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/persons/{person_id}")
async def delete_contact(person_id: str, current_user: User = Depends(get_current_user)):
    """Delete a contact for the current user"""
    try:
        # Check if the contact exists and belongs to the user, then delete
        delete_query = """
        DELETE FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        RETURNING id
        """
        
        result = await database.fetch_one(delete_query, {
            "contact_id": person_id,
            "user_id": current_user.id
        })
        
        if not result:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {"message": "Contact deleted successfully", "id": str(result["id"])}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# NEW SIMPLIFIED: Recent Contacts using timestamp field
@app.post("/recents/{contact_id}")
async def update_recent_contact(contact_id: str, current_user: User = Depends(get_current_user)):
    """Update last accessed time for a contact (simplified approach)"""
    try:
        # Verify contact exists and belongs to the user, then update timestamp
        update_query = """
        UPDATE crm_contacts 
        SET last_accessed_at = NOW(), updated_at = NOW()
        WHERE id = :contact_id AND user_id = :user_id
        RETURNING id
        """
        
        result = await database.fetch_one(update_query, {
            "contact_id": contact_id,
            "user_id": current_user.id
        })
        
        if not result:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        return {"message": "Contact access time updated", "contact_id": contact_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/recents")
async def get_recent_contacts(current_user: User = Depends(get_current_user)):
    """Get recent contacts for the current user (simplified approach - last 20 accessed)"""
    try:
        query = """
        SELECT id, name, email, created_at, updated_at, is_favorite, last_accessed_at
        FROM crm_contacts
        WHERE user_id = :user_id AND last_accessed_at IS NOT NULL
        ORDER BY last_accessed_at DESC
        LIMIT 20
        """
        
        results = await database.fetch_all(query, {"user_id": current_user.id})
        
        return [
            {
                "contact": {
                    "id": str(result["id"]),
                    "name": result["name"],
                    "email": result["email"] or "",
                    "created_at": result["created_at"].isoformat(),
                    "updated_at": result["updated_at"].isoformat(),
                    "is_favorite": result["is_favorite"]
                },
                "accessedAt": result["last_accessed_at"].isoformat()
            }
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/recents")
async def clear_recent_contacts(current_user: User = Depends(get_current_user)):
    """Clear all recent contacts for the current user (simplified approach)"""
    try:
        update_query = """
        UPDATE crm_contacts 
        SET last_accessed_at = NULL, updated_at = NOW()
        WHERE user_id = :user_id AND last_accessed_at IS NOT NULL
        """
        
        await database.execute(update_query, {"user_id": current_user.id})
        
        return {"message": "Recent contacts cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# NEW SIMPLIFIED: Favorites using boolean field
@app.post("/favorites/{contact_id}")
async def toggle_favorite_contact(contact_id: str, current_user: User = Depends(get_current_user)):
    """Toggle favorite status for a contact (simplified approach)"""
    try:
        # First verify the contact exists and belongs to the user
        contact_query = """
        SELECT id, is_favorite FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        """
        contact = await database.fetch_one(contact_query, {
            "contact_id": contact_id,
            "user_id": current_user.id
        })
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Toggle the favorite status
        new_favorite_status = not contact['is_favorite']
        
        update_query = """
        UPDATE crm_contacts 
        SET is_favorite = :is_favorite, updated_at = NOW()
        WHERE id = :contact_id AND user_id = :user_id
        """
        
        await database.execute(update_query, {
            "is_favorite": new_favorite_status,
            "contact_id": contact_id,
            "user_id": current_user.id
        })
        
        return {
            "message": f"Contact {'added to' if new_favorite_status else 'removed from'} favorites",
            "contact_id": contact_id,
            "is_favorite": new_favorite_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/favorites")
async def get_favorite_contacts(current_user: User = Depends(get_current_user)):
    """Get favorite contacts for the current user (simplified approach)"""
    try:
        query = """
        SELECT id, name, email, created_at, updated_at, is_favorite, last_accessed_at
        FROM crm_contacts
        WHERE user_id = :user_id AND is_favorite = true
        ORDER BY updated_at DESC
        """
        
        results = await database.fetch_all(query, {"user_id": current_user.id})
        
        return [
            {
                "id": str(result["id"]),
                "name": result["name"],
                "email": result["email"] or "",
                "created_at": result["created_at"].isoformat(),
                "updated_at": result["updated_at"].isoformat(),
                "is_favorite": result["is_favorite"],
                "last_accessed_at": result["last_accessed_at"].isoformat() if result["last_accessed_at"] else None
            }
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/favorites")
async def clear_favorite_contacts(current_user: User = Depends(get_current_user)):
    """Clear all favorite contacts for the current user (simplified approach)"""
    try:
        update_query = """
        UPDATE crm_contacts 
        SET is_favorite = false, updated_at = NOW()
        WHERE user_id = :user_id AND is_favorite = true
        """
        
        await database.execute(update_query, {"user_id": current_user.id})
        
        return {"message": "All favorite contacts cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint (public)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}