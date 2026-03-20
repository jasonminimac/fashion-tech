"""Shared FastAPI dependencies: DB session, current user."""
from typing import Generator
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from src.app.database.engine import SessionLocal
from src.app.utils.security import decode_token
from src.app.utils.errors import Unauthorized, NotFound
from src.app.models.user import User


def get_db() -> Generator[Session, None, None]:
    """Yield a DB session and ensure it is closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    authorization: str = Header(..., description="Bearer <access_token>"),
    db: Session = Depends(get_db),
) -> User:
    """Decode JWT bearer token and return the authenticated user.

    Raises:
        Unauthorized: if token is missing, malformed, or expired.
        NotFound: if the user no longer exists.
    """
    if not authorization.startswith("Bearer "):
        raise Unauthorized("Authorization header must start with 'Bearer '")
    
    token = authorization[len("Bearer "):]
    
    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise Unauthorized(str(exc))
    
    user_id: str = payload.get("sub")
    if not user_id:
        raise Unauthorized("Token missing subject claim")
    
    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if not user:
        raise NotFound("User not found")
    
    if not user.is_active:
        raise Unauthorized("Account is inactive")
    
    return user


def require_retailer(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires the user to have retailer/admin role.

    NOTE: extend with a role field on User model when roles are implemented.
    """
    # Placeholder: check a 'role' attribute when available
    role = getattr(current_user, "role", None)
    if role not in ("retailer", "admin"):
        from src.app.utils.errors import Forbidden
        raise Forbidden("Retailer role required")
    return current_user
