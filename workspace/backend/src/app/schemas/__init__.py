"""Schemas package."""
from src.app.schemas.base import BaseResponse, PaginatedResponse
from src.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from src.app.schemas.user import UserResponse, UserUpdate
from src.app.schemas.scan import ScanCreate, ScanResponse, UploadUrlResponse
from src.app.schemas.garment import GarmentResponse, GarmentCreate, CategoryResponse
from src.app.schemas.outfit import OutfitCreate, OutfitUpdate, OutfitResponse

__all__ = [
    "BaseResponse", "PaginatedResponse",
    "RegisterRequest", "LoginRequest", "TokenResponse", "RefreshRequest",
    "UserResponse", "UserUpdate",
    "ScanCreate", "ScanResponse", "UploadUrlResponse",
    "GarmentResponse", "GarmentCreate", "CategoryResponse",
    "OutfitCreate", "OutfitUpdate", "OutfitResponse",
]
