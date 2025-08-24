from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt
import uuid
import os
from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr
from databases import Database

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Pydantic models
class UserSignup(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    login: str  # Can be username or email
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    photo_url: Optional[str] = None
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class AuthService:
    def __init__(self, database: Database):
        self.db = database
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        query = """
        SELECT id, username, email, password, photo_url, created_at, updated_at
        FROM users WHERE username = :username
        """
        result = await self.db.fetch_one(query, {"username": username})
        return dict(result) if result else None
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = """
        SELECT id, username, email, password, photo_url, created_at, updated_at
        FROM users WHERE email = :email
        """
        result = await self.db.fetch_one(query, {"email": email})
        return dict(result) if result else None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
        SELECT id, username, email, password, photo_url, created_at, updated_at
        FROM users WHERE id = :user_id
        """
        result = await self.db.fetch_one(query, {"user_id": user_id})
        return dict(result) if result else None
    
    async def create_user(self, user_data: UserSignup, photo_filename: Optional[str] = None) -> str:
        """Create new user and return user ID"""
        user_id = str(uuid.uuid4())
        hashed_password = self.hash_password(user_data.password)
        photo_url = f"/uploads/{photo_filename}" if photo_filename else None
        
        query = """
        INSERT INTO users (id, username, email, password, photo_url, created_at, updated_at)
        VALUES (:id, :username, :email, :password, :photo_url, :created_at, :updated_at)
        """
        
        values = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "password": hashed_password,
            "photo_url": photo_url,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.db.execute(query, values)
        return user_id
    
    async def create_session(self, user_id: str, refresh_token: str) -> str:
        """Create new session and return session ID"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        query = """
        INSERT INTO sessions (id, user_id, refresh_token, created_at, expires_at, is_active)
        VALUES (:id, :user_id, :refresh_token, :created_at, :expires_at, :is_active)
        """
        
        values = {
            "id": session_id,
            "user_id": user_id,
            "refresh_token": refresh_token,
            "created_at": datetime.utcnow(),
            "expires_at": expires_at,
            "is_active": "true"
        }
        
        await self.db.execute(query, values)
        return session_id
    
    async def delete_user_sessions(self, user_id: str):
        """Delete all sessions for a user"""
        query = "DELETE FROM sessions WHERE user_id = :user_id"
        await self.db.execute(query, {"user_id": user_id})
    
    async def verify_session(self, refresh_token: str) -> bool:
        """Verify if refresh token exists and is active"""
        query = """
        SELECT id FROM sessions 
        WHERE refresh_token = :refresh_token 
        AND is_active = 'true' 
        AND expires_at > :current_time
        """
        result = await self.db.fetch_one(query, {
            "refresh_token": refresh_token,
            "current_time": datetime.utcnow()
        })
        return result is not None
    
    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password meets requirements"""
        import re
        
        errors = []
        
        if len(password) < 8:
            errors.append("Password must contain at least 8 characters")
            
        if not re.search(r'[A-Z]', password):
            errors.append("Password must include at least one uppercase letter (A-Z)")
            
        if not re.search(r'[a-z]', password):
            errors.append("Password must include at least one lowercase letter (a-z)")
            
        if not re.search(r'\d', password):
            errors.append("Password must include at least one numeric digit (0-9)")
            
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
            errors.append("Password must include at least one special character (!@#$%^&*)")
            
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password does not meet security requirements. Must contain at least 8 characters including uppercase, lowercase, numeric, and special characters."
            )

    async def signup(self, user_data: UserSignup, photo_filename: Optional[str] = None) -> TokenResponse:
        """Register a new user"""
        # Validate password requirements
        self.validate_password(user_data.password)
        
        # Check if username already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user_id = await self.create_user(user_data, photo_filename)
        
        # Create tokens
        token_data = {"sub": user_id, "username": user_data.username}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        # Create session
        await self.create_session(user_id, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def login(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Try to find user by email or username
        user = (await self.get_user_by_email(login_data.login) or 
                await self.get_user_by_username(login_data.login))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not self.verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        token_data = {"sub": str(user["id"]), "username": user["username"]}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        # Create session
        await self.create_session(str(user["id"]), refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, token: str) -> Dict[str, str]:
        """Logout user and invalidate session"""
        try:
            payload = self.verify_token(token)
            user_id = payload.get("sub")
            
            if user_id:
                await self.delete_user_sessions(user_id)
            
            return {"message": "Successfully logged out"}
        
        except HTTPException:
            return {"message": "Already logged out"}
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from token"""
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return User(
            id=str(user["id"]),
            username=user["username"],
            email=user["email"],
            photo_url=user.get("photo_url"),
            created_at=user["created_at"]
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        payload = self.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        # Verify session exists
        if not await self.verify_session(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session"
            )
        
        # Create new access token
        token_data = {"sub": user_id, "username": username}
        access_token = self.create_access_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )