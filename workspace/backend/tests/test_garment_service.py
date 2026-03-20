"""
Tests for garment_service: search, size recommendation, and upload validation.
Uses SQLite in-memory DB via SQLAlchemy for full ORM coverage.
"""

import uuid
import pytest
# Import directly from sqlalchemy.engine to avoid the conftest mock patch on sqlalchemy.create_engine
import sqlalchemy.engine as _sa_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models.base import BaseModel
from app.models.garment import Garment, GarmentSize, GarmentCategory, RetailPartner
from app.services.garment_service import (
    search_garments,
    recommend_size,
    validate_garment_upload,
)
from app.utils.errors import ValidationError, NotFoundError, GarmentError


# ─── DB Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def engine():
    eng = _sa_engine.create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    BaseModel.metadata.create_all(eng)
    return eng


@pytest.fixture()
def db(engine) -> Session:
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def brand(db) -> RetailPartner:
    b = RetailPartner(id=uuid.uuid4(), name="TestBrand", slug=f"testbrand-{uuid.uuid4().hex[:6]}")
    db.add(b)
    db.flush()
    return b


@pytest.fixture()
def category(db) -> GarmentCategory:
    c = GarmentCategory(id=uuid.uuid4(), name="Shirts", slug=f"shirts-{uuid.uuid4().hex[:6]}")
    db.add(c)
    db.flush()
    return c


def make_garment(db, brand, category, garment_type="shirt", fit_category="slim") -> Garment:
    g = Garment(
        id=uuid.uuid4(),
        sku=f"SKU-{uuid.uuid4().hex[:8]}",
        brand_id=brand.id,
        name="Test Shirt",
        garment_type=garment_type,
        fit_category=fit_category,
        model_file_key="garments/b/g/model.fbx",
        category_id=category.id,
    )
    db.add(g)
    db.flush()
    return g


def make_size(db, garment, label, chest_min, chest_max, order=0) -> GarmentSize:
    s = GarmentSize(
        id=uuid.uuid4(),
        garment_id=garment.id,
        size_label=label,
        size_order=order,
        chest_min_cm=chest_min,
        chest_max_cm=chest_max,
    )
    db.add(s)
    db.flush()
    return s


# ─── search_garments ─────────────────────────────────────────────────────────

class TestSearchGarments:
    def test_returns_all_active(self, db, brand, category):
        make_garment(db, brand, category, garment_type="shirt")
        make_garment(db, brand, category, garment_type="shirt")
        results = search_garments(db, category="shirt")
        assert len(results) >= 2

    def test_filter_by_category(self, db, brand, category):
        make_garment(db, brand, category, garment_type="jacket")
        make_garment(db, brand, category, garment_type="jeans")
        jackets = search_garments(db, category="jacket")
        assert all(g.garment_type == "jacket" for g in jackets)

    def test_filter_by_fit_type(self, db, brand, category):
        make_garment(db, brand, category, garment_type="shirt", fit_category="relaxed")
        make_garment(db, brand, category, garment_type="shirt", fit_category="slim")
        relaxed = search_garments(db, fit_type="relaxed")
        assert all(g.fit_category == "relaxed" for g in relaxed)

    def test_both_filters(self, db, brand, category):
        make_garment(db, brand, category, garment_type="trousers", fit_category="regular")
        results = search_garments(db, category="trousers", fit_type="regular")
        assert all(g.garment_type == "trousers" and g.fit_category == "regular" for g in results)

    def test_no_results_returns_empty(self, db, brand, category):
        results = search_garments(db, category="space-suit-nonexistent")
        assert results == []

    def test_limit_and_offset(self, db, brand, category):
        for _ in range(5):
            make_garment(db, brand, category, garment_type="socks")
        first_two = search_garments(db, category="socks", limit=2, offset=0)
        next_two = search_garments(db, category="socks", limit=2, offset=2)
        assert len(first_two) == 2
        assert len(next_two) == 2
        assert {g.id for g in first_two}.isdisjoint({g.id for g in next_two})

    def test_excludes_soft_deleted(self, db, brand, category):
        from datetime import datetime
        g = make_garment(db, brand, category, garment_type="deleted-type")
        g.deleted_at = datetime.utcnow()
        db.flush()
        results = search_garments(db, category="deleted-type")
        assert all(g2.deleted_at is None for g2 in results)


# ─── recommend_size ──────────────────────────────────────────────────────────

class SimpleUserScan:
    """Minimal scan measurement stub."""
    def __init__(self, chest_cm):
        self.chest_cm = chest_cm


class TestRecommendSize:
    def test_exact_match_s(self, db, brand, category):
        g = make_garment(db, brand, category)
        make_size(db, g, "XS", 76, 84, order=0)
        make_size(db, g, "S", 84, 92, order=1)
        make_size(db, g, "M", 92, 100, order=2)
        scan = SimpleUserScan(chest_cm=88.0)
        assert recommend_size(db, scan, g.id) == "S"

    def test_exact_match_m(self, db, brand, category):
        g = make_garment(db, brand, category)
        make_size(db, g, "S", 84, 92, order=1)
        make_size(db, g, "M", 92, 100, order=2)
        make_size(db, g, "L", 100, 108, order=3)
        scan = SimpleUserScan(chest_cm=95.0)
        assert recommend_size(db, scan, g.id) == "M"

    def test_boundary_value_inclusive(self, db, brand, category):
        g = make_garment(db, brand, category)
        make_size(db, g, "M", 92, 100, order=2)
        scan = SimpleUserScan(chest_cm=100.0)  # Upper boundary
        assert recommend_size(db, scan, g.id) == "M"

    def test_fallback_nearest_midpoint(self, db, brand, category):
        """When chest doesn't fit any range, return nearest by midpoint."""
        g = make_garment(db, brand, category)
        make_size(db, g, "S", 80, 88, order=0)
        make_size(db, g, "XL", 108, 116, order=3)
        scan = SimpleUserScan(chest_cm=75.0)  # Below S range
        result = recommend_size(db, scan, g.id)
        assert result == "S"

    def test_no_chest_raises_garment_error(self, db, brand, category):
        g = make_garment(db, brand, category)
        make_size(db, g, "M", 92, 100, order=0)
        scan = SimpleUserScan(chest_cm=None)
        with pytest.raises(GarmentError):
            recommend_size(db, scan, g.id)

    def test_no_sizes_raises_not_found(self, db, brand, category):
        g = make_garment(db, brand, category)
        scan = SimpleUserScan(chest_cm=90.0)
        with pytest.raises(NotFoundError):
            recommend_size(db, scan, g.id)


# ─── validate_garment_upload ─────────────────────────────────────────────────

class TestValidateGarmentUpload:
    def test_valid_data_returns_cleaned(self):
        data = {
            "name": "  Blue Shirt  ",
            "garment_type": "shirt",
            "model_file_key": "garments/b/g/model.fbx",
        }
        result = validate_garment_upload("brand-1", data)
        assert result["name"] == "Blue Shirt"  # stripped

    def test_missing_name_raises(self):
        with pytest.raises(ValidationError, match="name"):
            validate_garment_upload("brand-1", {
                "garment_type": "shirt",
                "model_file_key": "model.fbx",
            })

    def test_missing_garment_type_raises(self):
        with pytest.raises(ValidationError, match="garment_type"):
            validate_garment_upload("brand-1", {
                "name": "Shirt",
                "model_file_key": "model.fbx",
            })

    def test_missing_model_file_key_raises(self):
        with pytest.raises(ValidationError, match="model_file_key"):
            validate_garment_upload("brand-1", {
                "name": "Shirt",
                "garment_type": "shirt",
            })

    def test_invalid_file_extension_raises(self):
        with pytest.raises(ValidationError):
            validate_garment_upload("brand-1", {
                "name": "Shirt",
                "garment_type": "shirt",
                "model_file_key": "model.zip",
            })

    def test_valid_glb_extension(self):
        data = {
            "name": "Dress",
            "garment_type": "dress",
            "model_file_key": "garments/b/g/model.glb",
        }
        result = validate_garment_upload("brand-1", data)
        assert result["model_file_key"].endswith(".glb")

    def test_missing_brand_id_raises(self):
        with pytest.raises(ValidationError, match="brand_id"):
            validate_garment_upload("", {
                "name": "Shirt",
                "garment_type": "shirt",
                "model_file_key": "model.fbx",
            })

    def test_negative_price_raises(self):
        with pytest.raises(ValidationError, match="price"):
            validate_garment_upload("brand-1", {
                "name": "Shirt",
                "garment_type": "shirt",
                "model_file_key": "model.fbx",
                "price_usd": -10.0,
            })

    def test_valid_price_normalised(self):
        data = {
            "name": "Shirt",
            "garment_type": "shirt",
            "model_file_key": "model.fbx",
            "price_usd": "49.99",
        }
        result = validate_garment_upload("brand-1", data)
        assert result["price_usd"] == 49.99
