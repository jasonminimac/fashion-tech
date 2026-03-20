"""User profile routes: /users/me"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.dependencies import get_db, get_current_user
from src.app.models.user import User
from src.app.schemas.user import UserResponse, UserUpdate
from src.app.schemas.base import BaseResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=BaseResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user's profile."""
    return BaseResponse.success(UserResponse.model_validate(current_user).model_dump())


@router.put("/me", response_model=BaseResponse)
def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile fields."""
    update_data = payload.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return BaseResponse.success(UserResponse.model_validate(current_user).model_dump())


@router.delete("/me", response_model=BaseResponse)
def delete_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Soft-delete the current user account."""
    current_user.deleted_at = datetime.utcnow()
    current_user.is_active = False
    db.commit()
    return BaseResponse.success({"message": "Account deleted"})
