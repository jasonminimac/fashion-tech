"""Shared test fixtures for Fashion Tech API tests."""
import sys
from unittest.mock import MagicMock, patch
from uuid import uuid4
from datetime import datetime


# ---------------------------------------------------------------------------
# Patch psycopg2 + engine at import time so tests run without a real DB
# ---------------------------------------------------------------------------
if "psycopg2" not in sys.modules:
    sys.modules["psycopg2"] = MagicMock()
    sys.modules["psycopg2.extensions"] = MagicMock()
    sys.modules["psycopg2.extras"] = MagicMock()

_engine_patcher = patch("sqlalchemy.create_engine", return_value=MagicMock())
_engine_patcher.start()

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi import HTTPException


def build_test_app():
    """Build a minimal FastAPI app with all routers mounted."""
    app = FastAPI()

    @app.exception_handler(HTTPException)
    async def http_exc(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "data": None, "error": exc.detail},
        )

    from src.app.routers import (
        auth_router, users_router, scans_router,
        garments_router, outfits_router, health_router,
    )
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(scans_router)
    app.include_router(garments_router)
    app.include_router(outfits_router)
    app.include_router(health_router)
    return app


def make_user(
    user_id=None,
    email="test@example.com",
    password_hash=None,
    is_active=True,
    deleted_at=None,
    role=None,
):
    """Create a mock User ORM object."""
    from src.app.utils.security import hash_password
    user = MagicMock()
    user.id = user_id or uuid4()
    user.email = email
    user.password_hash = password_hash or hash_password("Password1")
    user.is_active = is_active
    user.deleted_at = deleted_at
    user.first_name = "Test"
    user.last_name = "User"
    user.avatar_url = None
    user.gender = None
    user.age_range = None
    user.height_cm = None
    user.preferred_fit = None
    user.email_verified = False
    user.created_at = datetime.utcnow()
    user.role = role
    return user


def make_mock_db(first_return=None, side_effect=None):
    """Create a mock SQLAlchemy Session."""
    mock_db = MagicMock()
    q = mock_db.query.return_value.filter.return_value
    if side_effect:
        q.first.side_effect = side_effect
    else:
        q.first.return_value = first_return
    return mock_db
