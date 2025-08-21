
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
    """Get all contacts for the current user from crm_contacts table"""
    try:
        query = """
        SELECT id, user_id, name, email, created_at, updated_at 
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
                "updated_at": contact["updated_at"]
            }
            for contact in contacts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/persons/{person_id}")
async def read_contact(person_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific contact by ID for the current user"""
    try:
        query = """
        SELECT id, user_id, name, email, created_at, updated_at 
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
            "updated_at": contact["updated_at"]
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

# Recent Contacts endpoints
@app.post("/recents/{contact_id}")
async def add_recent_contact(contact_id: str, current_user: User = Depends(get_current_user)):
    """Add or update a recent contact for the current user"""
    try:
        # First verify the contact exists and belongs to the user
        contact_query = """
        SELECT id FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        """
        contact = await database.fetch_one(contact_query, {
            "contact_id": contact_id,
            "user_id": current_user.id
        })
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Use UPSERT to add or update recent contact
        upsert_query = """
        INSERT INTO user_recent_contacts (user_id, contact_id, accessed_at)
        VALUES (:user_id, :contact_id, NOW())
        ON CONFLICT (user_id, contact_id)
        DO UPDATE SET accessed_at = NOW()
        """
        
        await database.execute(upsert_query, {
            "user_id": current_user.id,
            "contact_id": contact_id
        })
        
        return {"message": "Recent contact updated", "contact_id": contact_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/recents")
async def get_recent_contacts(current_user: User = Depends(get_current_user)):
    """Get recent contacts for the current user (limited to 20, ordered by most recent)"""
    try:
        query = """
        SELECT c.id, c.name, c.email, c.created_at, c.updated_at, r.accessed_at
        FROM user_recent_contacts r
        JOIN crm_contacts c ON r.contact_id = c.id
        WHERE r.user_id = :user_id
        ORDER BY r.accessed_at DESC
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
                    "updated_at": result["updated_at"].isoformat()
                },
                "accessedAt": result["accessed_at"].isoformat()
            }
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/recents")
async def clear_recent_contacts(current_user: User = Depends(get_current_user)):
    """Clear all recent contacts for the current user"""
    try:
        delete_query = """
        DELETE FROM user_recent_contacts 
        WHERE user_id = :user_id
        """
        
        await database.execute(delete_query, {"user_id": current_user.id})
        
        return {"message": "Recent contacts cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Favorites endpoints
@app.post("/favorites/{contact_id}")
async def add_favorite_contact(contact_id: str, current_user: User = Depends(get_current_user)):
    """Add a contact to favorites"""
    try:
        # First verify the contact exists and belongs to the user
        contact_query = """
        SELECT id FROM crm_contacts 
        WHERE id = :contact_id AND user_id = :user_id
        """
        contact = await database.fetch_one(contact_query, {
            "contact_id": contact_id,
            "user_id": current_user.id
        })
        
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        # Add to favorites (ignore if already exists)
        insert_query = """
        INSERT INTO user_favorites (user_id, contact_id, created_at)
        VALUES (:user_id, :contact_id, NOW())
        ON CONFLICT (user_id, contact_id) DO NOTHING
        """
        
        await database.execute(insert_query, {
            "user_id": current_user.id,
            "contact_id": contact_id
        })
        
        return {"message": "Contact added to favorites", "contact_id": contact_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/favorites/{contact_id}")
async def remove_favorite_contact(contact_id: str, current_user: User = Depends(get_current_user)):
    """Remove a contact from favorites"""
    try:
        delete_query = """
        DELETE FROM user_favorites 
        WHERE user_id = :user_id AND contact_id = :contact_id
        RETURNING contact_id
        """
        
        result = await database.fetch_one(delete_query, {
            "user_id": current_user.id,
            "contact_id": contact_id
        })
        
        if not result:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        return {"message": "Contact removed from favorites", "contact_id": contact_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/favorites")
async def get_favorite_contacts(current_user: User = Depends(get_current_user)):
    """Get favorite contacts for the current user"""
    try:
        query = """
        SELECT c.id, c.name, c.email, c.created_at, c.updated_at
        FROM user_favorites f
        JOIN crm_contacts c ON f.contact_id = c.id
        WHERE f.user_id = :user_id
        ORDER BY f.created_at DESC
        """
        
        results = await database.fetch_all(query, {"user_id": current_user.id})
        
        return [
            {
                "id": str(result["id"]),
                "name": result["name"],
                "email": result["email"] or "",
                "created_at": result["created_at"].isoformat(),
                "updated_at": result["updated_at"].isoformat()
            }
            for result in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/favorites")
async def clear_favorite_contacts(current_user: User = Depends(get_current_user)):
    """Clear all favorite contacts for the current user"""
    try:
        delete_query = """
        DELETE FROM user_favorites 
        WHERE user_id = :user_id
        """
        
        await database.execute(delete_query, {"user_id": current_user.id})
        
        return {"message": "Favorite contacts cleared"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Health check endpoint (public)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}