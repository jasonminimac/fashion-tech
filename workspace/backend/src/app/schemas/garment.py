"""Garment request/response schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class GarmentSizeResponse(BaseModel):
    """Size variant."""
    id: uuid.UUID
    size_label: str
    chest_min_cm: Optional[float] = None
    chest_max_cm: Optional[float] = None
    waist_min_cm: Optional[float] = None
    waist_max_cm: Optional[float] = None
    hips_min_cm: Optional[float] = None
    hips_max_cm: Optional[float] = None

    model_config = {"from_attributes": True}


class GarmentResponse(BaseModel):
    """Garment catalogue item."""
    id: uuid.UUID
    sku: str
    name: str
    description: Optional[str] = None
    garment_type: str
    fit_category: Optional[str] = None
    fabric_type: Optional[str] = None
    price_usd: Optional[float] = None
    retail_url: Optional[str] = None
    model_file_key: str
    sizes: List[GarmentSizeResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class GarmentCreate(BaseModel):
    """Create garment (retailer only)."""
    sku: str
    name: str
    description: Optional[str] = None
    garment_type: str
    category_id: Optional[uuid.UUID] = None
    fit_category: Optional[str] = None
    fabric_type: Optional[str] = None
    fabric_weight_gsm: Optional[float] = None
    fabric_stretch_percent: Optional[float] = None
    price_usd: Optional[float] = None
    retail_url: Optional[str] = None
    model_file_key: str


class CategoryResponse(BaseModel):
    """Garment category."""
    id: uuid.UUID
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

    model_config = {"from_attributes": True}
