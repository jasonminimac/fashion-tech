"""Outfit request/response schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class OutfitItemCreate(BaseModel):
    """Add a garment to an outfit."""
    garment_id: uuid.UUID
    garment_size_id: Optional[uuid.UUID] = None
    display_order: Optional[int] = None


class OutfitItemResponse(BaseModel):
    """Outfit item response."""
    id: uuid.UUID
    garment_id: uuid.UUID
    garment_size_id: Optional[uuid.UUID] = None
    display_order: Optional[int] = None

    model_config = {"from_attributes": True}


class OutfitCreate(BaseModel):
    """Create a new outfit."""
    scan_id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_private: bool = True
    occasions: Optional[str] = None
    mood: Optional[str] = None
    items: List[OutfitItemCreate] = []


class OutfitUpdate(BaseModel):
    """Update an outfit."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    occasions: Optional[str] = None
    mood: Optional[str] = None


class OutfitResponse(BaseModel):
    """Outfit response."""
    id: uuid.UUID
    user_id: uuid.UUID
    scan_id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_private: bool
    occasions: Optional[str] = None
    mood: Optional[str] = None
    preview_image_url: Optional[str] = None
    items: List[OutfitItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
