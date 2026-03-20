from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSON
from .base import BaseModel

class Garment(BaseModel):
    """3D clothing item in catalogue."""
    __tablename__ = "garments"

    sku = Column(String(100), unique=True, nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), 
                      ForeignKey("retail_partners.id", ondelete="CASCADE"))
    
    # Product info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(UUID(as_uuid=True), 
                         ForeignKey("garment_categories.id", ondelete="SET NULL"))
    garment_type = Column(String(50), nullable=False)
    
    # 3D model
    model_file_key = Column(String(500), nullable=False)
    texture_urls = Column(JSON)
    
    # Fit data
    fit_category = Column(String(50))
    fabric_type = Column(String(100))
    fabric_weight_gsm = Column(Float)
    fabric_stretch_percent = Column(Float)
    
    # Price & retail
    price_usd = Column(Float)
    retail_url = Column(String(500))
    
    # Soft delete
    deleted_at = Column(DateTime)
    
    # Relationships
    sizes = relationship("GarmentSize", back_populates="garment", cascade="all, delete-orphan")
    brand = relationship("RetailPartner", back_populates="garments")
    category = relationship("GarmentCategory", back_populates="garments")

    def __repr__(self):
        return f"<Garment(sku={self.sku}, name={self.name})>"


class GarmentSize(BaseModel):
    """Size variant of a garment with fit data."""
    __tablename__ = "garment_sizes"

    garment_id = Column(UUID(as_uuid=True), 
                        ForeignKey("garments.id", ondelete="CASCADE"), 
                        nullable=False)
    
    # Size info
    size_label = Column(String(50), nullable=False)
    size_order = Column(Integer)
    
    # Fit ranges (cm)
    chest_min_cm = Column(Float)
    chest_max_cm = Column(Float)
    waist_min_cm = Column(Float)
    waist_max_cm = Column(Float)
    hips_min_cm = Column(Float)
    hips_max_cm = Column(Float)
    
    garment = relationship("Garment", back_populates="sizes")


class GarmentCategory(BaseModel):
    """Taxonomy for browsing garments."""
    __tablename__ = "garment_categories"

    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("garment_categories.id"))
    sort_order = Column(Integer)
    
    # Hierarchical relationships — remote_side must reference the Column object
    children = relationship(
        "GarmentCategory",
        foreign_keys=[parent_id],
        back_populates="parent",
    )
    parent = relationship(
        "GarmentCategory",
        foreign_keys=[parent_id],
        remote_side="GarmentCategory.id",
        back_populates="children",
        overlaps="children",
    )
    garments = relationship("Garment", back_populates="category")

    def __repr__(self):
        return f"<GarmentCategory(name={self.name}, slug={self.slug})>"


class RetailPartner(BaseModel):
    """B2B retailer integration."""
    __tablename__ = "retail_partners"

    name = Column(String(100))
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    # API integration
    api_endpoint = Column(String(500))
    api_key_hash = Column(String(255))
    is_active = Column(Boolean, default=False)
    
    # Metadata
    contact_email = Column(String(255))
    integration_type = Column(String(50))
    
    # Relationships
    garments = relationship("Garment", back_populates="brand")

    def __repr__(self):
        return f"<RetailPartner(name={self.name})>"
