"""Tests for auth endpoints: register, login, refresh, protected route."""
from unittest.mock import MagicMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient
from tests.conftest import build_test_app, make_user

from src.app import dependencies as deps

app = build_test_app()
client = TestClient(app, raise_server_exceptions=False)


def _db_override(user=None, scan_result=None):
    """Return a FastAPI dependency override for get_db."""
    mock_db = MagicMock()
    def _get_db():
        yield mock_db
    return _get_db, mock_db


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

class TestRegister:
    def test_register_success(self):
        """New user registers and receives JWT tokens."""
        get_db_fn, mock_db = _db_override()
        # No existing user
        mock_db.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/register", json={
                "email": "new@example.com",
                "password": "Password1",
                "first_name": "Jane",
            })
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "success"
        assert "access_token" in body["data"]
        assert "refresh_token" in body["data"]

    def test_register_duplicate_email(self):
        """Duplicate email returns 409."""
        existing = make_user(email="dup@example.com")
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = existing

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/register", json={
                "email": "dup@example.com",
                "password": "Password1",
            })
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 409

    def test_register_weak_password(self):
        """Weak password returns 422."""
        resp = client.post("/auth/register", json={
            "email": "weak@example.com",
            "password": "short",
        })
        assert resp.status_code == 422

    def test_register_invalid_email(self):
        """Invalid email format returns 422."""
        resp = client.post("/auth/register", json={
            "email": "not-an-email",
            "password": "Password1",
        })
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self):
        """Valid credentials return token pair."""
        user = make_user(email="login@example.com")
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = user

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/login", json={
                "email": "login@example.com",
                "password": "Password1",
            })
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert "access_token" in body["data"]
        assert "refresh_token" in body["data"]

    def test_login_wrong_password(self):
        """Wrong password returns 401."""
        user = make_user(email="login@example.com")
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = user

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/login", json={
                "email": "login@example.com",
                "password": "WrongPass999",
            })
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 401

    def test_login_unknown_email(self):
        """Unknown email returns 401."""
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/login", json={
                "email": "ghost@example.com",
                "password": "Password1",
            })
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

class TestRefresh:
    def _make_refresh_token(self, user_id):
        from src.app.utils.security import create_refresh_token
        return create_refresh_token({"sub": str(user_id)})

    def test_refresh_success(self):
        """Valid refresh token returns new access token."""
        user = make_user()
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = user
        token = self._make_refresh_token(user.id)

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post("/auth/refresh", json={"refresh_token": token})
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert "access_token" in resp.json()["data"]

    def test_refresh_invalid_token(self):
        """Garbage refresh token returns 401."""
        resp = client.post("/auth/refresh", json={"refresh_token": "bad.token.here"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Protected route: GET /users/me
# ---------------------------------------------------------------------------

class TestProtectedRoute:
    def _token(self, user_id):
        from src.app.utils.security import create_access_token
        return create_access_token({"sub": str(user_id)})

    def test_no_token_returns_4xx(self):
        """No Authorization header → 422."""
        resp = client.get("/users/me")
        assert resp.status_code in (401, 422)

    def test_invalid_token_returns_401(self):
        """Garbage token → 401."""
        resp = client.get("/users/me", headers={"Authorization": "Bearer garbage"})
        assert resp.status_code == 401

    def test_valid_token_returns_200(self):
        """Valid JWT → 200 with user profile."""
        user = make_user(email="me@example.com")
        get_db_fn, mock_db = _db_override()
        mock_db.query.return_value.filter.return_value.first.return_value = user
        token = self._token(user.id)

        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "success"
        assert body["data"]["email"] == "me@example.com"


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_not_plaintext(self):
        from src.app.utils.security import hash_password, verify_password
        plain = "MySecret1"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        from src.app.utils.security import hash_password, verify_password
        hashed = hash_password("RightPass1")
        assert not verify_password("WrongPass1", hashed)
