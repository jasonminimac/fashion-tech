"""
Integration tests: end-to-end flow — register → scan → outfit.

Tests the full chain: auth → scan (S3 URL) → garment lookup → outfit creation.
Uses SQLite in-memory DB and moto for S3.
"""

import os
import uuid

import boto3
import pytest
from moto import mock_aws
# Use sqlalchemy.engine directly to avoid the conftest mock patch on sqlalchemy.create_engine
import sqlalchemy.engine as _sa_engine
from sqlalchemy.orm import sessionmaker, Session

os.environ.setdefault("JWT_SECRET_KEY", "integration-test-secret-key-xyz-abc-123")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")
os.environ.setdefault("AWS_REGION", "us-east-1")

from app.models.base import BaseModel
from app.models.user import User
from app.models.scan import Scan, ScanMeasurement
from app.models.garment import Garment, GarmentSize, GarmentCategory, RetailPartner
from app.models.outfit import Outfit, OutfitItem

from app.services.auth_service import hash_password, verify_password, create_jwt_token, decode_jwt_token
from app.services.s3_service import generate_signed_upload_url, generate_signed_download_url, scan_model_key, garment_model_key
from app.services.garment_service import search_garments, recommend_size
from app.services.outfit_service import create_outfit, list_outfits, update_outfit

S3_BUCKET = "integration-test-bucket"


# ─── Fixtures ─────────────────────────────────────────────────────────────────

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
def s3(monkeypatch):
    """Patch _get_s3_client to return a moto-backed client."""
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=S3_BUCKET)
        import app.services.s3_service as svc
        monkeypatch.setattr(svc, "_get_s3_client", lambda: client)
        yield client


# ─── Test: Full register → scan → outfit flow ────────────────────────────────

class TestRegisterScanOutfitFlow:
    """
    Simulates the full user journey:
      1. Register (hash password)
      2. Login (verify password → issue JWT)
      3. Decode JWT (authenticate)
      4. Generate S3 upload URL for scan
      5. Complete scan upload, store measurements
      6. Search garments and get recommendations
      7. Create an outfit with recommended garments
      8. List outfits, update outfit
    """

    def test_full_flow(self, db, s3):
        # ── Step 1: Register ──────────────────────────────────────────────
        email = f"user_{uuid.uuid4().hex[:8]}@example.com"
        plaintext_pw = "SecurePassword99!"
        hashed = hash_password(plaintext_pw)

        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hashed,
            first_name="Alice",
            last_name="Test",
        )
        db.add(user)
        db.flush()

        assert user.id is not None
        assert user.password_hash.startswith("$2b$")

        # ── Step 2: Login ─────────────────────────────────────────────────
        assert verify_password(plaintext_pw, user.password_hash) is True
        assert verify_password("WrongPassword", user.password_hash) is False

        # ── Step 3: Issue & verify JWT ────────────────────────────────────
        access_token = create_jwt_token(str(user.id), token_type="access")
        refresh_token = create_jwt_token(str(user.id), token_type="refresh")

        decoded_user_id = decode_jwt_token(access_token)
        assert decoded_user_id == str(user.id)

        decoded_refresh = decode_jwt_token(refresh_token)
        assert decoded_refresh == str(user.id)

        # ── Step 4: Generate S3 scan upload URL ───────────────────────────
        scan_id = str(uuid.uuid4())
        key = scan_model_key(str(user.id), scan_id)
        assert key == f"scans/{user.id}/{scan_id}/model.glb"

        upload_url = generate_signed_upload_url(S3_BUCKET, key, expires_in=300)
        assert upload_url.startswith("http")
        assert S3_BUCKET in upload_url

        # ── Step 5: Store scan + measurements ────────────────────────────
        scan = Scan(
            id=uuid.uuid4(),
            user_id=user.id,
            scan_type="lidar",
            scan_file_key=key,
            status="complete",
        )
        db.add(scan)
        db.flush()

        measurement = ScanMeasurement(
            id=uuid.uuid4(),
            scan_id=scan.id,
            chest_cm=94.0,
            waist_cm=80.0,
            hips_cm=98.0,
        )
        db.add(measurement)
        db.flush()

        # ── Step 6: Create garments + search ─────────────────────────────
        brand = RetailPartner(id=uuid.uuid4(), name="BrandA", slug=f"branda-{uuid.uuid4().hex[:6]}")
        cat = GarmentCategory(id=uuid.uuid4(), name="Shirts", slug=f"shirts-{uuid.uuid4().hex[:6]}")
        db.add(brand)
        db.add(cat)
        db.flush()

        garment1 = Garment(
            id=uuid.uuid4(),
            sku=f"SKU-{uuid.uuid4().hex[:8]}",
            brand_id=brand.id,
            name="Classic White Shirt",
            garment_type="shirt",
            fit_category="slim",
            model_file_key=garment_model_key(str(brand.id), str(uuid.uuid4())),
            category_id=cat.id,
        )
        db.add(garment1)
        db.flush()

        size_s = GarmentSize(id=uuid.uuid4(), garment_id=garment1.id, size_label="S", size_order=0, chest_min_cm=84, chest_max_cm=92)
        size_m = GarmentSize(id=uuid.uuid4(), garment_id=garment1.id, size_label="M", size_order=1, chest_min_cm=92, chest_max_cm=100)
        size_l = GarmentSize(id=uuid.uuid4(), garment_id=garment1.id, size_label="L", size_order=2, chest_min_cm=100, chest_max_cm=108)
        db.add_all([size_s, size_m, size_l])
        db.flush()

        # Search returns the garment
        results = search_garments(db, category="shirt", fit_type="slim")
        assert any(g.id == garment1.id for g in results)

        # Recommend size for user (chest=94 → M range 92–100)
        recommended = recommend_size(db, measurement, garment1.id)
        assert recommended == "M"

        # ── Step 7: Generate download URL for garment ─────────────────────
        dl_url = generate_signed_download_url(S3_BUCKET, garment1.model_file_key, expires_in=3600)
        assert dl_url.startswith("http")
        assert "?" in dl_url  # Has signed params

        # ── Step 8: Create outfit ─────────────────────────────────────────
        outfit = create_outfit(
            db,
            user_id=user.id,
            name="My First Outfit",
            garment_ids=[garment1.id],
            scan_id=scan.id,
        )
        assert outfit.id is not None
        assert outfit.name == "My First Outfit"
        assert len(outfit.items) == 1
        assert outfit.items[0].garment_id == garment1.id

        # ── Step 9: List outfits ──────────────────────────────────────────
        outfits = list_outfits(db, user_id=user.id)
        assert any(o.id == outfit.id for o in outfits)

        # ── Step 10: Update outfit ────────────────────────────────────────
        updated = update_outfit(
            db,
            outfit_id=outfit.id,
            user_id=user.id,
            data={"name": "Updated Outfit Name"},
        )
        assert updated.name == "Updated Outfit Name"

        db.commit()


class TestAuthIsolation:
    """Auth edge cases in an integration context."""

    def test_different_users_get_different_tokens(self):
        uid1 = str(uuid.uuid4())
        uid2 = str(uuid.uuid4())
        t1 = create_jwt_token(uid1)
        t2 = create_jwt_token(uid2)
        assert decode_jwt_token(t1) == uid1
        assert decode_jwt_token(t2) == uid2
        assert t1 != t2

    def test_access_and_refresh_tokens_decode_same_user(self):
        uid = str(uuid.uuid4())
        access = create_jwt_token(uid, "access")
        refresh = create_jwt_token(uid, "refresh")
        assert decode_jwt_token(access) == uid
        assert decode_jwt_token(refresh) == uid

    def test_password_hashes_differ_for_same_password(self):
        pw = "SharedPassword1!"
        h1 = hash_password(pw)
        h2 = hash_password(pw)
        assert h1 != h2
        assert verify_password(pw, h1)
        assert verify_password(pw, h2)


class TestS3IntegrationPaths:
    def test_scan_upload_then_download_url(self, s3):
        uid, sid = str(uuid.uuid4()), str(uuid.uuid4())
        key = scan_model_key(uid, sid)
        upload = generate_signed_upload_url(S3_BUCKET, key, 300)
        download = generate_signed_download_url(S3_BUCKET, key, 3600)
        assert upload != download
        assert S3_BUCKET in upload
        assert S3_BUCKET in download

    def test_garment_url_has_fbx_path(self, s3):
        bid, gid = str(uuid.uuid4()), str(uuid.uuid4())
        key = garment_model_key(bid, gid)
        url = generate_signed_download_url(S3_BUCKET, key)
        assert "garments" in url
        assert "fbx" in url
