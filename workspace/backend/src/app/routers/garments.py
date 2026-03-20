"""Garment routes: catalogue browse + B2B create."""
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.app.dependencies import get_db, get_current_user, require_retailer
from src.app.models.garment import Garment, GarmentCategory
from src.app.models.user import User
from src.app.schemas.garment import GarmentResponse, GarmentCreate, CategoryResponse
from src.app.schemas.base import BaseResponse, PaginatedResponse
from src.app.utils.errors import NotFound
from src.app.utils.validators import clamp_pagination

router = APIRouter(prefix="/garments", tags=["garments"])


@router.get("/categories", response_model=BaseResponse)
def list_categories(db: Session = Depends(get_db)):
    """List all garment categories."""
    categories = db.query(GarmentCategory).order_by(GarmentCategory.sort_order).all()
    return BaseResponse.success(
        [CategoryResponse.model_validate(c).model_dump() for c in categories]
    )


@router.get("", response_model=PaginatedResponse)
def list_garments(
    category: Optional[str] = Query(None, description="Category slug filter"),
    fit: Optional[str] = Query(None, description="Fit category filter"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all garments, filterable by category slug and fit category."""
    limit, offset = clamp_pagination(limit, offset)

    query = db.query(Garment).filter(Garment.deleted_at.is_(None))

    if category:
        cat = db.query(GarmentCategory).filter(GarmentCategory.slug == category).first()
        if cat:
            query = query.filter(Garment.category_id == cat.id)

    if fit:
        query = query.filter(Garment.fit_category == fit)

    total = query.count()
    garments = query.order_by(Garment.name).offset(offset).limit(limit).all()

    return PaginatedResponse(
        data=[GarmentResponse.model_validate(g).model_dump() for g in garments],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{garment_id}", response_model=BaseResponse)
def get_garment(garment_id: uuid.UUID, db: Session = Depends(get_db)):
    """Get garment details by ID."""
    garment = db.query(Garment).filter(
        Garment.id == garment_id,
        Garment.deleted_at.is_(None),
    ).first()
    if not garment:
        raise NotFound("Garment not found")
    return BaseResponse.success(GarmentResponse.model_validate(garment).model_dump())


@router.post("", response_model=BaseResponse, status_code=201)
def create_garment(
    payload: GarmentCreate,
    current_user: User = Depends(require_retailer),
    db: Session = Depends(get_db),
):
    """Create a garment (retailer/admin role required)."""
    garment = Garment(**payload.model_dump())
    db.add(garment)
    db.commit()
    db.refresh(garment)
    return BaseResponse.success(GarmentResponse.model_validate(garment).model_dump())
