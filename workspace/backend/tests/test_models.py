"""
tests/test_models.py — ORM relationship and instantiation tests.

These tests use an in-memory SQLite database (no PostgreSQL required) to verify:
  - All models instantiate without errors
  - Foreign key / cascade relationships are correctly defined
  - Relationship traversal works (e.g., user.scans, scan.measurements)
  - RetailerAPIAccess consent logic

Run with:
    pytest tests/test_models.py -v
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT / "src"))

# Use SQLite in-memory so no external Postgres is needed for unit tests
TEST_DB_URL = "sqlite:///:memory:"

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
from app.models import (  # noqa: E402
    Base,
    User,
    SessionToken,
    Scan,
    ScanMeasurement,
    Garment,
    GarmentSize,
    GarmentCategory,
    RetailPartner,
    Outfit,
    OutfitItem,
    SavedFavouriteGarment,
    RetailerAPIAccess,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def db_engine():
    """Create an in-memory SQLite engine with all tables.

    We bypass any global mock of sqlalchemy.create_engine by importing
    the real one directly from the sqlalchemy package.
    """
    import importlib
    import sqlalchemy as _sa

    # The conftest patches sqlalchemy.create_engine — grab the real one directly
    real_create_engine = importlib.import_module("sqlalchemy.engine.create").create_engine
    from sqlalchemy import event as sa_event

    eng = real_create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})

    @sa_event.listens_for(eng, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture
def db(db_engine) -> Session:
    """Yield a fresh session, rolling back after each test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def make_user(email: str = "test@example.com", **kwargs) -> User:
    return User(
        email=email,
        password_hash="$2b$12$fakehash",
        first_name="Test",
        last_name="User",
        **kwargs,
    )


def make_partner(slug: str = "test-brand") -> RetailPartner:
    return RetailPartner(name="Test Brand", slug=slug, is_active=True)


def make_category(slug: str = "tops") -> GarmentCategory:
    return GarmentCategory(name="Tops", slug=slug)


def make_garment(sku: str = "TOP-001", **kwargs) -> Garment:
    return Garment(
        sku=sku,
        name="Test Shirt",
        garment_type="shirt",
        model_file_key=f"garments/test/{sku}/model.glb",
        fit_category="structured",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Tests — Model instantiation
# ---------------------------------------------------------------------------


class TestInstantiation:
    """All models should instantiate without errors."""

    def test_user_instantiates(self):
        u = make_user()
        assert u.email == "test@example.com"
        # is_active has a Python-side default that fires at INSERT, not on __init__
        assert u.is_active in (True, None)

    def test_session_token_instantiates(self):
        st = SessionToken(
            user_id=uuid4(),
            token_family="fam-abc",
            expires_at=datetime.now(tz=timezone.utc) + timedelta(days=7),
        )
        assert st.token_family == "fam-abc"
        # is_revoked default fires at INSERT, not on __init__
        assert st.is_revoked in (False, None)

    def test_scan_instantiates(self):
        s = Scan(user_id=uuid4(), scan_type="lidar")
        # status default fires at INSERT, not on __init__
        assert s.status in ("pending", None)

    def test_scan_measurement_instantiates(self):
        m = ScanMeasurement(scan_id=uuid4(), chest_cm=92.0, waist_cm=76.0)
        assert m.chest_cm == 92.0

    def test_garment_instantiates(self):
        g = make_garment()
        assert g.sku == "TOP-001"
        assert g.fit_category == "structured"

    def test_garment_size_instantiates(self):
        gs = GarmentSize(garment_id=uuid4(), size_label="M", size_order=3)
        assert gs.size_label == "M"

    def test_garment_category_instantiates(self):
        cat = make_category()
        assert cat.slug == "tops"

    def test_retail_partner_instantiates(self):
        rp = make_partner()
        assert rp.is_active is True

    def test_outfit_instantiates(self):
        o = Outfit(user_id=uuid4(), scan_id=uuid4(), name="Summer Look")
        assert o.name == "Summer Look"
        # is_private default fires at INSERT, not on __init__
        assert o.is_private in (True, None)

    def test_outfit_item_instantiates(self):
        oi = OutfitItem(outfit_id=uuid4(), garment_id=uuid4(), display_order=1)
        assert oi.display_order == 1

    def test_saved_favourite_garment_instantiates(self):
        sfg = SavedFavouriteGarment(user_id=uuid4(), garment_id=uuid4())
        assert sfg is not None

    def test_retailer_api_access_instantiates(self):
        raa = RetailerAPIAccess(
            user_id=uuid4(),
            retail_partner_id=uuid4(),
            is_active=False,
        )
        assert raa.is_active is False
        assert raa.has_active_consent is False


# ---------------------------------------------------------------------------
# Tests — DB persistence and relationships
# ---------------------------------------------------------------------------


class TestPersistence:
    """Verify objects persist and IDs are assigned."""

    def test_user_persists(self, db: Session):
        u = make_user(email="persist@example.com")
        db.add(u)
        db.flush()
        assert u.id is not None

    def test_garment_with_sizes_persists(self, db: Session):
        partner = make_partner(slug="brand-x")
        cat = make_category(slug="bottoms")
        db.add_all([partner, cat])
        db.flush()

        g = make_garment(sku="BOT-TEST-001")
        g.brand_id = partner.id
        g.category_id = cat.id
        db.add(g)
        db.flush()

        for label, order in [("S", 1), ("M", 2), ("L", 3)]:
            db.add(GarmentSize(garment_id=g.id, size_label=label, size_order=order))
        db.flush()

        fetched = db.query(Garment).filter_by(sku="BOT-TEST-001").one()
        assert len(fetched.sizes) == 3
        assert fetched.brand.name == "Test Brand"
        assert fetched.category.slug == "bottoms"


class TestRelationships:
    """Verify ORM relationship traversal."""

    def test_user_scans_relationship(self, db: Session):
        user = make_user(email="scan-user@example.com")
        db.add(user)
        db.flush()

        scan = Scan(user_id=user.id, scan_type="lidar")
        db.add(scan)
        db.flush()

        # Traverse relationship
        assert len(user.scans) == 1
        assert user.scans[0].scan_type == "lidar"

    def test_scan_measurements_relationship(self, db: Session):
        user = make_user(email="meas-user@example.com")
        db.add(user)
        db.flush()

        scan = Scan(user_id=user.id, scan_type="photogrammetry")
        db.add(scan)
        db.flush()

        measurement = ScanMeasurement(
            scan_id=scan.id,
            chest_cm=96.0,
            waist_cm=80.0,
            hips_cm=100.0,
        )
        db.add(measurement)
        db.flush()

        assert len(scan.measurements) == 1
        assert scan.measurements[0].chest_cm == 96.0
        # Back-reference
        assert scan.measurements[0].scan.user_id == user.id

    def test_outfit_items_relationship(self, db: Session):
        user = make_user(email="outfit-user@example.com")
        db.add(user)
        db.flush()

        scan = Scan(user_id=user.id, scan_type="lidar")
        db.add(scan)
        db.flush()

        partner = make_partner(slug="outfit-brand")
        db.add(partner)
        db.flush()

        g1 = make_garment(sku="G-OUTFIT-001")
        g1.brand_id = partner.id
        g2 = make_garment(sku="G-OUTFIT-002")
        g2.brand_id = partner.id
        db.add_all([g1, g2])
        db.flush()

        outfit = Outfit(user_id=user.id, scan_id=scan.id, name="Test Outfit")
        db.add(outfit)
        db.flush()

        db.add(OutfitItem(outfit_id=outfit.id, garment_id=g1.id, display_order=1))
        db.add(OutfitItem(outfit_id=outfit.id, garment_id=g2.id, display_order=2))
        db.flush()

        assert len(outfit.items) == 2
        assert outfit.user.email == "outfit-user@example.com"

    def test_user_outfits_relationship(self, db: Session):
        user = make_user(email="multi-outfit@example.com")
        db.add(user)
        db.flush()

        scan = Scan(user_id=user.id, scan_type="lidar")
        db.add(scan)
        db.flush()

        for i in range(3):
            db.add(Outfit(user_id=user.id, scan_id=scan.id, name=f"Outfit {i}"))
        db.flush()

        assert len(user.outfits) == 3

    def test_retailer_api_access_consent(self, db: Session):
        user = make_user(email="consent-user@example.com")
        db.add(user)
        db.flush()

        partner = make_partner(slug="consent-brand")
        db.add(partner)
        db.flush()

        # Before consent
        access = RetailerAPIAccess(
            user_id=user.id,
            retail_partner_id=partner.id,
            is_active=False,
        )
        db.add(access)
        db.flush()
        assert access.has_active_consent is False

        # After consent
        access.consent_at = datetime.utcnow()
        access.is_active = True
        db.flush()
        assert access.has_active_consent is True

        # After withdrawal
        access.consent_withdrawn_at = datetime.utcnow()
        assert access.has_active_consent is False

    def test_cascade_delete_user_scans(self, db: Session):
        user = make_user(email="cascade@example.com")
        db.add(user)
        db.flush()

        scan = Scan(user_id=user.id, scan_type="lidar")
        db.add(scan)
        db.flush()
        scan_id = scan.id

        db.delete(user)
        db.flush()

        assert db.query(Scan).filter_by(id=scan_id).first() is None


# ---------------------------------------------------------------------------
# Tests — __repr__
# ---------------------------------------------------------------------------


class TestRepr:
    """Spot-check __repr__ output for clarity."""

    def test_user_repr(self):
        u = make_user()
        assert "test@example.com" in repr(u)

    def test_garment_repr(self):
        g = make_garment(sku="REPR-001")
        assert "REPR-001" in repr(g)

    def test_retail_partner_repr(self):
        rp = make_partner()
        assert "Test Brand" in repr(rp)

    def test_retailer_api_access_repr(self):
        raa = RetailerAPIAccess(
            user_id=uuid4(), retail_partner_id=uuid4(), is_active=True
        )
        assert "RetailerAPIAccess" in repr(raa)
