"""Routers package — export all APIRouter instances."""
from src.app.routers.auth import router as auth_router
from src.app.routers.users import router as users_router
from src.app.routers.scans import router as scans_router
from src.app.routers.garments import router as garments_router
from src.app.routers.outfits import router as outfits_router
from src.app.routers.retailers import router as retailers_router
from src.app.routers.health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "scans_router",
    "garments_router",
    "outfits_router",
    "retailers_router",
    "health_router",
]
