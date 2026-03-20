"""Tests for garment endpoints."""
from unittest.mock import MagicMock
from uuid import uuid4
from fastapi.testclient import TestClient
from tests.conftest import build_test_app, make_user
from src.app import dependencies as deps

app = build_test_app()
client = TestClient(app, raise_server_exceptions=False)


def _auth_headers(user_id):
    from src.app.utils.security import create_access_token
    token = create_access_token({"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _db_with_user(user=None):
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = user
    mock_db.query.return_value.filter.return_value.count.return_value = 0
    mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
    mock_db.query.return_value.order_by.return_value.all.return_value = []
    def _get_db():
        yield mock_db
    return _get_db, mock_db


class TestListGarments:
    def test_list_returns_200(self):
        """Garment listing is public — no auth required."""
        get_db_fn, _ = _db_with_user()
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.get("/garments")
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_limit_over_100_rejected(self):
        """Query param limit > 100 returns 422."""
        resp = client.get("/garments?limit=500")
        assert resp.status_code == 422


class TestGetGarment:
    def test_not_found_returns_404(self):
        get_db_fn, _ = _db_with_user(user=None)
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.get(f"/garments/{uuid4()}")
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 404


class TestListCategories:
    def test_returns_empty_list(self):
        get_db_fn, _ = _db_with_user()
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.get("/garments/categories")
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 200
        assert resp.json()["data"] == []


class TestCreateGarment:
    def test_no_auth_returns_4xx(self):
        resp = client.post("/garments", json={
            "sku": "TEST-001", "name": "Test Shirt",
            "garment_type": "top", "model_file_key": "models/t.glb",
        })
        assert resp.status_code in (401, 422)

    def test_non_retailer_returns_403(self):
        """User without retailer role gets 403."""
        user = make_user()  # role=None
        get_db_fn, _ = _db_with_user(user=user)
        app.dependency_overrides[deps.get_db] = get_db_fn
        try:
            resp = client.post(
                "/garments",
                headers=_auth_headers(user.id),
                json={
                    "sku": "TEST-001", "name": "Test Shirt",
                    "garment_type": "top", "model_file_key": "models/t.glb",
                },
            )
        finally:
            app.dependency_overrides.clear()

        assert resp.status_code == 403
