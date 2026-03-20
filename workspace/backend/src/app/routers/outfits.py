"""Outfit CRUD routes."""
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.app.dependencies import get_db, get_current_user
from src.app.models.outfit import Outfit, OutfitItem
from src.app.models.user import User
from src.app.schemas.outfit import OutfitCreate, OutfitUpdate, OutfitResponse
from src.app.schemas.base import BaseResponse, PaginatedResponse
from src.app.utils.errors import NotFound, Forbidden
from src.app.utils.validators import clamp_pagination

router = APIRouter(prefix="/outfits", tags=["outfits"])


@router.post("", response_model=BaseResponse, status_code=201)
def create_outfit(
    payload: OutfitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new outfit for the current user."""
    outfit = Outfit(
        user_id=current_user.id,
        scan_id=payload.scan_id,
        name=payload.name,
        description=payload.description,
        is_private=payload.is_private,
        occasions=payload.occasions,
        mood=payload.mood,
    )
    db.add(outfit)
    db.flush()

    for item_data in payload.items:
        item = OutfitItem(
            outfit_id=outfit.id,
            garment_id=item_data.garment_id,
            garment_size_id=item_data.garment_size_id,
            display_order=item_data.display_order,
        )
        db.add(item)

    db.commit()
    db.refresh(outfit)
    return BaseResponse.success(OutfitResponse.model_validate(outfit).model_dump())


@router.get("", response_model=PaginatedResponse)
def list_outfits(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List the current user's outfits."""
    limit, offset = clamp_pagination(limit, offset)
    query = db.query(Outfit).filter(
        Outfit.user_id == current_user.id,
        Outfit.deleted_at.is_(None),
    )
    total = query.count()
    outfits = query.order_by(Outfit.created_at.desc()).offset(offset).limit(limit).all()

    return PaginatedResponse(
        data=[OutfitResponse.model_validate(o).model_dump() for o in outfits],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{outfit_id}", response_model=BaseResponse)
def get_outfit(
    outfit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get outfit by ID (owner only)."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.deleted_at.is_(None),
    ).first()
    if not outfit:
        raise NotFound("Outfit not found")
    if str(outfit.user_id) != str(current_user.id):
        raise Forbidden("Cannot access this outfit")
    return BaseResponse.success(OutfitResponse.model_validate(outfit).model_dump())


@router.put("/{outfit_id}", response_model=BaseResponse)
def update_outfit(
    outfit_id: uuid.UUID,
    payload: OutfitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an outfit (owner only)."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.deleted_at.is_(None),
    ).first()
    if not outfit:
        raise NotFound("Outfit not found")
    if str(outfit.user_id) != str(current_user.id):
        raise Forbidden("Cannot modify this outfit")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(outfit, field, value)

    db.commit()
    db.refresh(outfit)
    return BaseResponse.success(OutfitResponse.model_validate(outfit).model_dump())


@router.delete("/{outfit_id}", response_model=BaseResponse)
def delete_outfit(
    outfit_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete an outfit (owner only)."""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.deleted_at.is_(None),
    ).first()
    if not outfit:
        raise NotFound("Outfit not found")
    if str(outfit.user_id) != str(current_user.id):
        raise Forbidden("Cannot delete this outfit")

    outfit.deleted_at = datetime.utcnow()
    db.commit()
    return BaseResponse.success({"message": "Outfit deleted"})
