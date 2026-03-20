"""Tests for user profile endpoints."""
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from tests.conftest import build_test_app, make_user
from src.app import dependencies as deps

app = build_test_app()
client = TestClient(app, raise_server_exceptions=False)


def _auth_headers(user_id):
    from src.app.utils.security import create_access_token
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _db_override(user=None):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = user
    def _get_db():
        yield mock_db
    return _get_db, mock_db


class TestGetMe:
    def test_get_me_returns_profile(self):
        user = make_user(email="profile@example.com")
        get_db_fn, _ = _db_override(user)
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.get("/users/me", headers=_auth_headers(user.id))
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["data"]["email"] == "profile@example.com"

    def test_get_me_no_auth(self):
        resp = client.get("/users/me")
        assert resp.status_code in (401, 422)


class TestUpdateMe:
    def test_update_me_success(self):
        user = make_user()
        get_db_fn, _ = _db_override(user)
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.put(
                "/users/me",
                headers=_auth_headers(user.id),
                json={"first_name": "Updated", "height_cm": 175},
            )
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200

    def test_update_me_no_auth(self):
        resp = client.put("/users/me", json={"first_name": "X"})
        assert resp.status_code in (401, 422)


class TestDeleteMe:
    def test_soft_deletes_user(self):
        user = make_user()
        get_db_fn, _ = _db_override(user)
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.delete("/users/me", headers=_auth_headers(user.id))
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["status"] == "success"

    def test_delete_me_no_auth(self):
        resp = client.delete("/users/me")
        assert resp.status_code in (401, 422)
