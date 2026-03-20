from sqlalchemy import Column, String, Float, DateTime, Text, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from datetime import datetime
from .base import BaseModel

class Scan(BaseModel):
    """3D body scan metadata and files."""
    __tablename__ = "scans"

    user_id = Column(UUID(as_uuid=True), 
                     ForeignKey("users.id", ondelete="CASCADE"), 
                     nullable=False, index=True)
    
    # Scan info
    name = Column(String(255), default="My Scan")
    scan_type = Column(String(50), nullable=False)  # lidar, photogrammetry
    
    # File paths (S3)
    scan_file_key = Column(String(500))
    rigged_file_key = Column(String(500))
    
    # Processing status
    status = Column(String(50), default="pending")  # pending, processing, complete, failed
    error_message = Column(Text)
    
    # Metadata
    body_shape = Column(String(100))
    confidence_score = Column(Float)
    
    # Soft delete
    deleted_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    measurements = relationship("ScanMeasurement", 
                               back_populates="scan", 
                               cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(user_id={self.user_id}, id={self.id}, status={self.status})>"


class ScanMeasurement(BaseModel):
    """Body measurements derived from scan."""
    __tablename__ = "scan_measurements"

    scan_id = Column(UUID(as_uuid=True), 
                     ForeignKey("scans.id", ondelete="CASCADE"), 
                     nullable=False)
    
    # Measurements (cm)
    chest_cm = Column(Float)
    waist_cm = Column(Float)
    hips_cm = Column(Float)
    inseam_cm = Column(Float)
    shoulder_width_cm = Column(Float)
    arm_length_cm = Column(Float)
    torso_length_cm = Column(Float)
    
    # Additional
    weight_kg = Column(Float)
    bmi = Column(Float)
    fit_profile_notes = Column(Text)
    
    scan = relationship("Scan", back_populates="measurements")
