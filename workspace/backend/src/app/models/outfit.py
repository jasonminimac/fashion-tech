from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from .base import BaseModel

class Outfit(BaseModel):
    """Saved outfit combining body scan + garments."""
    __tablename__ = "outfits"

    user_id = Column(UUID(as_uuid=True), 
                     ForeignKey("users.id", ondelete="CASCADE"), 
                     nullable=False, index=True)
    scan_id = Column(UUID(as_uuid=True), 
                     ForeignKey("scans.id", ondelete="CASCADE"), 
                     nullable=False)
    
    # Outfit details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_private = Column(Boolean, default=True)
    
    # Metadata
    occasions = Column(String(500))
    mood = Column(String(100))
    
    # Preview
    preview_image_url = Column(String(500))
    
    # Soft delete
    deleted_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="outfits")
    scan = relationship("Scan", backref="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Outfit(user_id={self.user_id}, name={self.name})>"


class OutfitItem(BaseModel):
    """Individual garment in an outfit."""
    __tablename__ = "outfit_items"

    outfit_id = Column(UUID(as_uuid=True), 
                       ForeignKey("outfits.id", ondelete="CASCADE"), 
                       nullable=False)
    garment_id = Column(UUID(as_uuid=True), 
                        ForeignKey("garments.id", ondelete="CASCADE"), 
                        nullable=False)
    garment_size_id = Column(UUID(as_uuid=True), 
                             ForeignKey("garment_sizes.id", ondelete="SET NULL"))
    
    # Placement & display
    display_order = Column(Integer)
    
    outfit = relationship("Outfit", back_populates="items")
    garment = relationship("Garment", backref="outfit_items")
    garment_size = relationship("GarmentSize", backref="outfit_items")


class SavedFavouriteGarment(BaseModel):
    """User's bookmarked garments."""
    __tablename__ = "saved_favourite_garments"

    user_id = Column(UUID(as_uuid=True), 
                     ForeignKey("users.id", ondelete="CASCADE"), 
                     nullable=False, index=True)
    garment_id = Column(UUID(as_uuid=True), 
                        ForeignKey("garments.id", ondelete="CASCADE"), 
                        nullable=False)
    
    user = relationship("User", back_populates="saved_garments")
    garment = relationship("Garment", backref="saved_by")
