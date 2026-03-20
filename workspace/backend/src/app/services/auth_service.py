"""
Auth Service — password hashing and JWT token management.

Uses bcrypt (12 rounds) for passwords and HS256 JWT for tokens.

Environment variables required:
    JWT_SECRET_KEY  — Secret for signing tokens (generate: openssl rand -hex 32)
    JWT_ALGORITHM   — (optional) Defaults to "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES  — (optional) Defaults to 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS    — (optional) Defaults to 7
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Literal

import bcrypt
import jwt

from app.utils.errors import AuthError

logger = logging.getLogger(__name__)

_JWT_ALGORITHM = "HS256"


def _secret_key() -> str:
    key = os.environ.get("JWT_SECRET_KEY")
    if not key:
        raise AuthError("JWT_SECRET_KEY environment variable is not set", code="CONFIG_ERROR")
    return key


def _access_expiry_minutes() -> int:
    return int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def _refresh_expiry_days() -> int:
    return int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# ─── Password Hashing ────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (12 rounds).

    Args:
        password: Plaintext password string.

    Returns:
        bcrypt hash string (includes salt; safe to store).

    Raises:
        ValidationError: If password is empty.

    Example:
        hashed = hash_password("MySecret123!")
        # → "$2b$12$..."
    """
    if not password:
        from app.utils.errors import ValidationError
        raise ValidationError("Password must not be empty")
    rounds = int(os.environ.get("BCRYPT_ROUNDS", "12"))
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        password: Plaintext password to check.
        hashed:   bcrypt hash string (from hash_password).

    Returns:
        True if the password matches, False otherwise.

    Example:
        ok = verify_password("MySecret123!", stored_hash)
        if not ok:
            raise AuthError("Invalid credentials")
    """
    if not password or not hashed:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT Tokens ──────────────────────────────────────────────────────────────

TokenType = Literal["access", "refresh"]


def create_jwt_token(
    user_id: str,
    token_type: TokenType = "access",
) -> str:
    """Create a signed JWT for the given user.

    Args:
        user_id:    User identifier (UUID string).
        token_type: "access" (1 h) or "refresh" (7 d).

    Returns:
        Signed JWT string.

    Raises:
        AuthError: If JWT_SECRET_KEY is not configured.

    Example:
        token = create_jwt_token("user-uuid-123", "access")
    """
    now = datetime.now(timezone.utc)
    if token_type == "access":
        expire = now + timedelta(minutes=_access_expiry_minutes())
    elif token_type == "refresh":
        expire = now + timedelta(days=_refresh_expiry_days())
    else:
        from app.utils.errors import ValidationError
        raise ValidationError(f"Unknown token_type: {token_type!r}")

    payload = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": expire,
    }
    token = jwt.encode(payload, _secret_key(), algorithm=_JWT_ALGORITHM)
    logger.debug("Created %s token for user %s (exp=%s)", token_type, user_id, expire)
    return token


def decode_jwt_token(token: str) -> str:
    """Decode and validate a JWT, returning the user_id (sub claim).

    Args:
        token: JWT string.

    Returns:
        user_id (str) from the token's "sub" claim.

    Raises:
        AuthError: If the token is invalid, expired, or malformed.

    Example:
        user_id = decode_jwt_token(access_token)
    """
    try:
        payload = jwt.decode(
            token,
            _secret_key(),
            algorithms=[_JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise AuthError("Token missing subject claim", code="INVALID_TOKEN")
        return user_id
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired", code="TOKEN_EXPIRED") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError(f"Invalid token: {exc}", code="INVALID_TOKEN") from exc
