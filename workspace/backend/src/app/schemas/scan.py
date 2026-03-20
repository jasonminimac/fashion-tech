"""Scan request/response schemas."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid


class ScanCreate(BaseModel):
    """Create a new scan record."""
    name: Optional[str] = "My Scan"
    scan_type: str  # lidar | photogrammetry


class MeasurementResponse(BaseModel):
    """Body measurements from scan."""
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    inseam_cm: Optional[float] = None
    shoulder_width_cm: Optional[float] = None
    arm_length_cm: Optional[float] = None
    torso_length_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None

    model_config = {"from_attributes": True}


class ScanResponse(BaseModel):
    """Scan record response."""
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    scan_type: str
    status: str
    body_shape: Optional[str] = None
    confidence_score: Optional[float] = None
    measurements: List[MeasurementResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadUrlResponse(BaseModel):
    """Pre-signed S3 upload URL."""
    upload_url: str
    key: str
    expires_in: int = 3600
