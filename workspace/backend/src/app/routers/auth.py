"""Auth routes: register, login, refresh."""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.app.models.user import User
from src.app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from src.app.schemas.base import BaseResponse
from src.app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from src.app.utils.errors import Conflict, Unauthorized, ValidationError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=BaseResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account.

    - Hashes password with bcrypt (rounds=12)
    - Returns JWT access + refresh tokens
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise Conflict("Email already registered")

    user = User(
        email=payload.email,
        password_hash=hash_password(payload.password),
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return BaseResponse.success(
        TokenResponse(access_token=access_token, refresh_token=refresh_token).model_dump()
    )


@router.post("/login", response_model=BaseResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate with email + password, return token pair."""
    user = db.query(User).filter(
        User.email == payload.email,
        User.deleted_at.is_(None),
    ).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise Unauthorized("Invalid email or password")

    if not user.is_active:
        raise Unauthorized("Account is inactive")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return BaseResponse.success(
        TokenResponse(access_token=access_token, refresh_token=refresh_token).model_dump()
    )


@router.post("/refresh", response_model=BaseResponse)
def refresh_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    try:
        token_data = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise Unauthorized(str(exc))

    user_id = token_data.get("sub")
    if not user_id:
        raise Unauthorized("Invalid refresh token")

    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None),
        User.is_active == True,
    ).first()
    if not user:
        raise Unauthorized("User not found or inactive")

    new_access_token = create_access_token({"sub": str(user.id)})

    return BaseResponse.success({"access_token": new_access_token, "token_type": "bearer"})
