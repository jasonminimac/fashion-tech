from fastapi import APIRouter
from models.garment import GarmentListResponse

router = APIRouter(prefix="/garments", tags=["garments"])


@router.get("", response_model=GarmentListResponse)
async def list_garments():
    """Stub: return an empty garment list."""
    return GarmentListResponse(garments=[], total=0)
