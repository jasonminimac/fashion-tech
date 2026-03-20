"""User request/response schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


class UserResponse(BaseModel):
    """Public user profile."""
    id: uuid.UUID
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    height_cm: Optional[int] = None
    preferred_fit: Optional[str] = None
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Updatable user fields."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    height_cm: Optional[int] = None
    preferred_fit: Optional[str] = None
    receives_marketing: Optional[bool] = None
