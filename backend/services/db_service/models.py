from sqlalchemy import Column, String, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
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
            "updated_at": self.updated_at
        }

class UserRecentContact(Base):
    __tablename__ = "user_recent_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=False, index=True)
    accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure one record per user-contact pair (will update accessed_at on re-access)
    __table_args__ = (UniqueConstraint('user_id', 'contact_id', name='unique_user_contact_recent'),)
    
    # Relationships
    user = relationship("User")
    contact = relationship("Contact")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id),
            "contact_id": str(self.contact_id),
            "accessed_at": self.accessed_at
        }

class UserFavorite(Base):
    __tablename__ = "user_favorites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    contact_id = Column(UUID(as_uuid=True), ForeignKey("crm_contacts.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Ensure one record per user-contact pair
    __table_args__ = (UniqueConstraint('user_id', 'contact_id', name='unique_user_contact_favorite'),)
    
    # Relationships
    user = relationship("User")
    contact = relationship("Contact")
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id), 
            "contact_id": str(self.contact_id),
            "created_at": self.created_at
        }