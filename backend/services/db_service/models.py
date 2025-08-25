from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Hashed password
    photo_url = Column(String(500), nullable=True)  # Path to photo file
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Contacts
    contacts = relationship("Contact", back_populates="user")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "photo_url": self.photo_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(String(10), default="true", nullable=False)  # Using string for simplicity

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "refresh_token": self.refresh_token,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "is_active": self.is_active == "true"
        }

class Contact(Base):
    __tablename__ = "crm_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # New simplified fields
    is_favorite = Column(Boolean, default=False, nullable=False, index=True)
    last_accessed_at = Column(DateTime, nullable=True, index=True)

    # Relationship to User
    user = relationship("User", back_populates="contacts")

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "name": self.name,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_favorite": self.is_favorite,
            "last_accessed_at": self.last_accessed_at
        }



class ActionRecording(Base):
    """Model for storing action audio recording metadata"""
    __tablename__ = "action_recordings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    
    # File information
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Processing status
    status = Column(String(50), default='uploaded', nullable=False, index=True)
    
    # Metadata
    format = Column(String(50), nullable=True)  # audio/webm, audio/wav, etc.
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    contact = relationship("Contact")
    context_recordings = relationship("ContextRecording", back_populates="action_recording")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "title": self.title,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "duration": self.duration,
            "status": self.status,
            "format": self.format,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ContextRecording(Base):
    """Model for storing context audio recording metadata (linked to action recordings)"""
    __tablename__ = "context_recordings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=True, index=True)
    action_recording_id = Column(UUID(as_uuid=True), ForeignKey("action_recordings.id"), nullable=False, index=True)
    
    # File information
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    duration = Column(Float, nullable=True)  # Duration in seconds
    
    # Processing status
    status = Column(String(50), default='uploaded', nullable=False, index=True)
    
    # Metadata
    format = Column(String(50), nullable=True)  # audio/webm, audio/wav, etc.
    sample_rate = Column(Integer, nullable=True)
    channels = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    contact = relationship("Contact")
    action_recording = relationship("ActionRecording", back_populates="context_recordings")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "contact_id": str(self.contact_id) if self.contact_id else None,
            "action_recording_id": str(self.action_recording_id),
            "title": self.title,
            "filename": self.filename,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "duration": self.duration,
            "status": self.status,
            "format": self.format,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class ApprovedEmail(Base):
    """Simplified table for approved emails with only action and context recording references"""
    __tablename__ = "approved_emails"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=False)
    
    # Recording references - only action and context
    action_recording_id = Column(UUID(as_uuid=True), ForeignKey("action_recordings.id"), nullable=True, index=True)
    context_recording_id = Column(UUID(as_uuid=True), ForeignKey("context_recordings.id"), nullable=True, index=True)
    
    email_content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    contact = relationship("Contact")
    action_recording = relationship("ActionRecording")
    context_recording = relationship("ContextRecording")
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "contact_id": str(self.contact_id),
            "action_recording_id": str(self.action_recording_id) if self.action_recording_id else None,
            "context_recording_id": str(self.context_recording_id) if self.context_recording_id else None,
            "email_content": self.email_content,
            "created_at": self.created_at,
            "has_action_audio": bool(self.action_recording_id),
            "has_context_audio": bool(self.context_recording_id)
        }
