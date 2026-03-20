"""Pydantic validators and helper functions for Fashion Tech API."""
import re
from typing import Optional


def validate_email(email: str) -> str:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_password(password: str) -> str:
    """Validate password strength: min 8 chars, 1 uppercase, 1 number."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one number")
    return password


def sanitize_string(value: Optional[str], max_length: int = 255) -> Optional[str]:
    """Strip whitespace and truncate to max_length."""
    if value is None:
        return None
    return value.strip()[:max_length]


def clamp_pagination(limit: int, offset: int) -> tuple[int, int]:
    """Clamp pagination params to safe ranges."""
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    return limit, offset
