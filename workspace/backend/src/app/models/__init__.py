"""
SQLAlchemy ORM models for Fashion Tech platform.

All models inherit from BaseModel (id, created_at, updated_at).

Data ownership rules:
- Platform owns all body scans (Scan, ScanMeasurement).
- Retailers get read-only access to fit profiles via RetailerAPIAccess.
- Raw mesh / scan_file_key are NEVER exposed to retailers.
"""

from .base import Base, BaseModel
from .user import User, SessionToken
from .scan import Scan, ScanMeasurement
from .garment import Garment, GarmentSize, GarmentCategory, RetailPartner
from .outfit import Outfit, OutfitItem, SavedFavouriteGarment
from .retailer import RetailerAPIAccess

__all__ = [
    # Base
    "Base",
    "BaseModel",
    # User
    "User",
    "SessionToken",
    # Scan
    "Scan",
    "ScanMeasurement",
    # Garment
    "Garment",
    "GarmentSize",
    "GarmentCategory",
    "RetailPartner",
    # Outfit
    "Outfit",
    "OutfitItem",
    "SavedFavouriteGarment",
    # Retailer
    "RetailerAPIAccess",
]
