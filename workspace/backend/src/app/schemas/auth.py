"""Auth request/response schemas."""
from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from src.app.utils.validators import validate_email, validate_password


class RegisterRequest(BaseModel):
    """User registration payload."""
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return validate_email(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return validate_password(v)


class LoginRequest(BaseModel):
    """Login credentials."""
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        return v.lower()


class TokenResponse(BaseModel):
    """JWT token pair returned after auth."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Refresh token payload."""
    refresh_token: str
