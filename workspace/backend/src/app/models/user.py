from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .base import BaseModel

class User(BaseModel):
    """User account with profile and authentication."""
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    avatar_url = Column(String(500))
    
    # Profile metadata
    gender = Column(String(50))
    age_range = Column(String(50))
    height_cm = Column(Integer)
    preferred_fit = Column(String(50))
    
    # Settings
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    receives_marketing = Column(Boolean, default=True)
    
    # Timestamps
    last_login_at = Column(DateTime)
    deleted_at = Column(DateTime)
    
    # Relationships
    scans = relationship("Scan", back_populates="user", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    saved_garments = relationship("SavedFavouriteGarment", 
                                 back_populates="user", 
                                 cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email={self.email}, id={self.id})>"


class SessionToken(BaseModel):
    """Refresh token tracking for JWT rotation."""
    __tablename__ = "session_tokens"

    user_id = Column(UUID(as_uuid=True), 
                     ForeignKey("users.id", ondelete="CASCADE"), 
                     nullable=False)
    token_family = Column(String(255), nullable=False, unique=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", backref="session_tokens")
