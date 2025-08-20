
import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.db_service import database, connect_db, disconnect_db, create_tables
from services.authservice import AuthService, UserSignup, UserLogin, TokenResponse, User

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

# Original endpoints (now protected)
@app.get("/persons")
async def read_persons(current_user: User = Depends(get_current_user)):
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]

@app.get("/persons/{person_id}")
async def read_person(person_id: int, current_user: User = Depends(get_current_user)):
    persons = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]
    for person in persons:
        if person["id"] == person_id:
            return person
    return {"error": "Person not found"}

# Health check endpoint (public)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}