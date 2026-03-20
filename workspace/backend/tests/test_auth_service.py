"""
Tests for auth_service: password hashing and JWT token management.
"""

import os
import time
import uuid

import pytest

# Ensure JWT_SECRET_KEY is set before importing service
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-abc123xyz")


from app.services.auth_service import (
    hash_password,
    verify_password,
    create_jwt_token,
    decode_jwt_token,
)
from app.utils.errors import AuthError, ValidationError


# ─── hash_password ───────────────────────────────────────────────────────────

class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("MyPassword1!")
        assert isinstance(result, str)

    def test_starts_with_bcrypt_prefix(self):
        result = hash_password("MyPassword1!")
        assert result.startswith("$2b$")

    def test_different_hash_each_call(self):
        """Same password must produce different hash (salt randomness)."""
        h1 = hash_password("SamePassword")
        h2 = hash_password("SamePassword")
        assert h1 != h2

    def test_cannot_reverse(self):
        """Hash should not contain the plaintext."""
        password = "SecretPass99"
        h = hash_password(password)
        assert password not in h

    def test_empty_password_raises(self):
        with pytest.raises(ValidationError):
            hash_password("")


# ─── verify_password ─────────────────────────────────────────────────────────

class TestVerifyPassword:
    def test_correct_password_returns_true(self):
        pw = "CorrectHorseBattery"
        h = hash_password(pw)
        assert verify_password(pw, h) is True

    def test_wrong_password_returns_false(self):
        h = hash_password("CorrectHorseBattery")
        assert verify_password("WrongPassword", h) is False

    def test_empty_password_returns_false(self):
        h = hash_password("SomePw")
        assert verify_password("", h) is False

    def test_empty_hash_returns_false(self):
        assert verify_password("SomePw", "") is False

    def test_case_sensitive(self):
        h = hash_password("password")
        assert verify_password("PASSWORD", h) is False


# ─── create_jwt_token ────────────────────────────────────────────────────────

class TestCreateJwtToken:
    def test_returns_string(self):
        token = create_jwt_token("user-123")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_access_token_default(self):
        token = create_jwt_token("user-1")
        # Should not raise
        user_id = decode_jwt_token(token)
        assert user_id == "user-1"

    def test_refresh_token(self):
        token = create_jwt_token("user-2", token_type="refresh")
        user_id = decode_jwt_token(token)
        assert user_id == "user-2"

    def test_uuid_user_id(self):
        uid = str(uuid.uuid4())
        token = create_jwt_token(uid)
        assert decode_jwt_token(token) == uid

    def test_invalid_token_type_raises(self):
        with pytest.raises(Exception):
            create_jwt_token("user-1", token_type="supertoken")  # type: ignore

    def test_no_secret_key_raises(self):
        original = os.environ.pop("JWT_SECRET_KEY", None)
        try:
            with pytest.raises(AuthError, match="JWT_SECRET_KEY"):
                create_jwt_token("user-1")
        finally:
            if original:
                os.environ["JWT_SECRET_KEY"] = original
            else:
                os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-unit-tests-abc123xyz"


# ─── decode_jwt_token ────────────────────────────────────────────────────────

class TestDecodeJwtToken:
    def test_valid_access_token(self):
        token = create_jwt_token("user-abc")
        assert decode_jwt_token(token) == "user-abc"

    def test_valid_refresh_token(self):
        token = create_jwt_token("user-xyz", token_type="refresh")
        assert decode_jwt_token(token) == "user-xyz"

    def test_tampered_token_raises(self):
        token = create_jwt_token("user-1")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(AuthError):
            decode_jwt_token(tampered)

    def test_random_string_raises(self):
        with pytest.raises(AuthError):
            decode_jwt_token("not.a.token")

    def test_expired_token_raises(self, monkeypatch):
        """Token with past expiry should raise AuthError with TOKEN_EXPIRED code."""
        import jwt as pyjwt
        from datetime import datetime, timezone, timedelta

        payload = {
            "sub": "user-expired",
            "type": "access",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = pyjwt.encode(payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256")
        with pytest.raises(AuthError) as exc_info:
            decode_jwt_token(expired_token)
        assert exc_info.value.code == "TOKEN_EXPIRED"

    def test_wrong_secret_raises(self):
        import jwt as pyjwt
        from datetime import datetime, timezone, timedelta

        payload = {
            "sub": "user-1",
            "type": "access",
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }
        token = pyjwt.encode(payload, "wrong-secret", algorithm="HS256")
        with pytest.raises(AuthError):
            decode_jwt_token(token)
