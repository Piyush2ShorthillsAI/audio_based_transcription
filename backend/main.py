
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
from services.audio_service import AudioServiceMinimal
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

# Initialize AudioService
def get_audio_service():
    return AudioServiceMinimal(database)

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

# =============================================================================
# AUDIO PROCESSING ENDPOINTS
# =============================================================================

@app.post("/audio/upload")
async def upload_audio(
    audio: UploadFile = File(...),
    title: str = Form(...),
    contact_id: Optional[str] = Form(None),
    audio_type: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    audio_service: AudioServiceMinimal = Depends(get_audio_service)
):
    """Upload an audio file for processing"""
    try:
        # Validate file type
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Validate file size (max 50MB)
        if hasattr(audio, 'size') and audio.size > 50 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 50MB")
        
        # Save audio file
        result = await audio_service.save_audio_file(
            audio_file=audio,
            user_id=current_user.id,
            title=title,
            contact_id=contact_id,
            audio_type=audio_type
        )
        
        return {
            "message": "Audio uploaded successfully",
            "recording_id": result["recording_id"],
            "filename": result["filename"],
            "file_size": result["file_size"],
            "duration": result["duration"],
            "status": result["status"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload audio: {str(e)}")

@app.post("/audio/generate-dual-email")
async def generate_dual_audio_email(
    request: dict,
    current_user: User = Depends(get_current_user),
    audio_service: AudioServiceMinimal = Depends(get_audio_service)
):
    """Generate professional email directly from dual audio files using Gemini 2.5 Pro"""
    try:
        # Debug: Print the entire request
        print(f"DEBUG: Full request received: {request}")
        print(f"DEBUG: Request keys: {list(request.keys())}")
        
        # Try both parameter naming conventions
        relationship_recording_id = (
            request.get("action_recording_id") or 
            request.get("relationship_recording_id")
        )
        content_recording_id = (
            request.get("context_recording_id") or 
            request.get("content_recording_id")
        )
        
        print(f"DEBUG: relationship_recording_id = {relationship_recording_id}")
        print(f"DEBUG: content_recording_id = {content_recording_id}")
        
        contact_id = request.get("contact_id")
        recipient_name = request.get("recipient_name", "")
        recipient_email = request.get("recipient_email", "")

        if not relationship_recording_id or not content_recording_id:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing recording IDs. Got relationship: {relationship_recording_id}, content: {content_recording_id}"
            )

        # Get contact info if contact_id provided
        if contact_id:
            print(f"DEBUG: Looking up contact {contact_id}")
            contact_query = """
            SELECT name, email FROM crm_contacts
            WHERE id = :contact_id AND user_id = :user_id
            """
            contact_result = await database.fetch_one(contact_query, {
                "contact_id": contact_id,
                "user_id": current_user.id
            })

            if contact_result:
                recipient_name = contact_result["name"]
                recipient_email = contact_result["email"]
                print(f"DEBUG: Found contact: {recipient_name} <{recipient_email}>")

        print("DEBUG: About to call audio service...")
        
        # Generate email using DIRECT audio processing
        result = await audio_service.generate_email_from_dual_audio_direct(
            relationship_recording_id=relationship_recording_id,
            content_recording_id=content_recording_id,
            user_id=current_user.id,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            relationship="professional"
        )

        print("DEBUG: Audio service completed successfully")
        return {
            "message": "Email generated successfully from direct audio processing",
            "email": result["email"],
            "analysis": result.get("analysis", {}),
            "processing_method": result["processing_method"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR in generate_dual_audio_email: {str(e)}")
        import traceback
        print("FULL STACK TRACE:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate email: {str(e)}")


@app.post("/emails/approve")
async def save_approved_email(request: dict, current_user: User = Depends(get_current_user)):
    """Save approved email with three foreign keys"""
    try:
        contact_id = request.get("contact_id")
        recording_id = request.get("recording_id")  # Single recording ID
        email_content = request.get("email_content")
        
        if not all([contact_id, recording_id, email_content]):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Insert into approved_emails table
        query = """
        INSERT INTO approved_emails (id, user_id, contact_id, recording_id, email_content, created_at)
        VALUES (:id, :user_id, :contact_id, :recording_id, :email_content, NOW())
        """
        
        await database.execute(query, {
            "id": str(uuid.uuid4()),
            "user_id": current_user.id,
            "contact_id": contact_id,
            "recording_id": recording_id,
            "email_content": email_content
        })
        
        return {"message": "Email approved and saved"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emails/approved")
async def get_approved_emails(
    contact_id: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get approved emails for the current user with new recording structure"""
    try:
        if contact_id:
            # Get approved emails for specific contact
            query = """
            SELECT id, contact_id, action_recording_id, context_recording_id, 
                   email_content, created_at
            FROM approved_emails 
            WHERE user_id = :user_id AND contact_id = :contact_id
            ORDER BY created_at DESC
            """
            emails = await database.fetch_all(query, {
                "user_id": current_user.id,
                "contact_id": contact_id
            })
        else:
            # Get all approved emails for user
            query = """
            SELECT id, contact_id, action_recording_id, context_recording_id,
                   email_content, created_at
            FROM approved_emails 
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            """
            emails = await database.fetch_all(query, {"user_id": current_user.id})
        
        # Convert to list of dictionaries and add recording info
        email_list = []
        for email in emails:
            email_dict = dict(email)
            # Add recording type info for better UI display
            email_dict["has_action_audio"] = bool(email_dict.get("action_recording_id"))
            email_dict["has_context_audio"] = bool(email_dict.get("context_recording_id"))
            # For backward compatibility, set recording_id to action_recording_id if it exists
            email_dict["recording_id"] = email_dict.get("action_recording_id") or email_dict.get("context_recording_id")
            email_list.append(email_dict)
        
        return {"emails": email_list}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audio/recordings")
async def get_audio_recordings(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    audio_service: AudioServiceMinimal = Depends(get_audio_service)
):
    """Get all audio recordings for the current user"""
    try:
        recordings = await audio_service.get_user_recordings(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "recordings": recordings,
            "total": len(recordings),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recordings: {str(e)}")

@app.get("/audio/recordings/{recording_id}")
async def get_audio_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get details for a specific audio recording from action or context tables"""
    try:
        # Try action_recordings first
        action_query = """
        SELECT *, 'action' as audio_type FROM action_recordings 
        WHERE id = :recording_id AND user_id = :user_id
        """
        recording = await database.fetch_one(action_query, {
            "recording_id": recording_id,
            "user_id": current_user.id
        })
        
        # If not found in action_recordings, try context_recordings
        if not recording:
            context_query = """
            SELECT *, 'context' as audio_type FROM context_recordings 
            WHERE id = :recording_id AND user_id = :user_id
            """
            recording = await database.fetch_one(context_query, {
                "recording_id": recording_id,
                "user_id": current_user.id
            })
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        return dict(recording)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recording: {str(e)}")

@app.delete("/audio/recordings/{recording_id}")
async def delete_audio_recording(
    recording_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete an audio recording from action or context tables"""
    try:
        import os
        from pathlib import Path
        
        # First, find the recording to get the file path
        action_query = """
        SELECT id, file_path FROM action_recordings 
        WHERE id = :recording_id AND user_id = :user_id
        """
        recording = await database.fetch_one(action_query, {
            "recording_id": recording_id,
            "user_id": current_user.id
        })
        
        table_name = "action_recordings"
        
        # If not found in action_recordings, try context_recordings
        if not recording:
            context_query = """
            SELECT id, file_path FROM context_recordings 
            WHERE id = :recording_id AND user_id = :user_id
            """
            recording = await database.fetch_one(context_query, {
                "recording_id": recording_id,
                "user_id": current_user.id
            })
            table_name = "context_recordings"
        
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        
        file_path = recording['file_path']
        
        # Delete the database record
        delete_query = f"""
        DELETE FROM {table_name} 
        WHERE id = :recording_id AND user_id = :user_id
        """
        
        rows_deleted = await database.execute(delete_query, {
            "recording_id": recording_id,
            "user_id": current_user.id
        })
        
        if rows_deleted == 0:
            raise HTTPException(status_code=404, detail="Recording not found or could not be deleted")
        
        # Delete the physical file
        try:
            if file_path:
                full_path = Path(file_path)
                if not full_path.is_absolute():
                    # If relative path, make it relative to backend directory
                    full_path = Path(__file__).parent / file_path
                
                if full_path.exists():
                    full_path.unlink()
                    print(f"✅ Deleted file: {full_path}")
                else:
                    print(f"⚠️ File not found for deletion: {full_path}")
        except Exception as file_error:
            print(f"⚠️ Error deleting file {file_path}: {str(file_error)}")
            # Don't fail the entire operation if file deletion fails
        
        return {
            "message": "Recording deleted successfully",
            "recording_id": recording_id,
            "table": table_name
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete recording: {str(e)}")

@app.get("/contacts/{contact_id}/audio")
async def get_contact_audio_recordings(
    contact_id: str,
    audio_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get all audio recordings associated with a specific contact from both action and context tables"""
    try:
        recordings = []
        
        # Get recordings based on audio_type filter
        if audio_type == "action":
            # Only action recordings
            action_query = """
            SELECT *, 'action' as audio_type FROM action_recordings 
            WHERE contact_id = :contact_id AND user_id = :user_id
            ORDER BY created_at DESC
            """
            action_recordings = await database.fetch_all(action_query, {
                "contact_id": contact_id,
                "user_id": current_user.id
            })
            recordings = list(action_recordings)
            
        elif audio_type == "context":
            # Only context recordings
            context_query = """
            SELECT *, 'context' as audio_type FROM context_recordings 
            WHERE contact_id = :contact_id AND user_id = :user_id
            ORDER BY created_at DESC
            """
            context_recordings = await database.fetch_all(context_query, {
                "contact_id": contact_id,
                "user_id": current_user.id
            })
            recordings = list(context_recordings)
            
        else:
            # Get all recordings from both tables
            action_query = """
            SELECT *, 'action' as audio_type FROM action_recordings 
            WHERE contact_id = :contact_id AND user_id = :user_id
            ORDER BY created_at DESC
            """
            context_query = """
            SELECT *, 'context' as audio_type FROM context_recordings 
            WHERE contact_id = :contact_id AND user_id = :user_id
            ORDER BY created_at DESC
            """
            
            action_recordings = await database.fetch_all(action_query, {
                "contact_id": contact_id,
                "user_id": current_user.id
            })
            
            context_recordings = await database.fetch_all(context_query, {
                "contact_id": contact_id,
                "user_id": current_user.id
            })
            
            # Combine and sort by creation time
            all_recordings = list(action_recordings) + list(context_recordings)
            recordings = sorted(all_recordings, key=lambda x: x['created_at'], reverse=True)
        
        return {
            "contact_id": contact_id,
            "audio_type": audio_type,
            "recordings": [dict(recording) for recording in recordings],
            "total": len(recordings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contact recordings: {str(e)}")

# Health check endpoint (public)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}