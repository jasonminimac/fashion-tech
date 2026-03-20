#!/usr/bin/env python3
"""
seed_garments.py — Insert test data into local PostgreSQL.

Creates:
  - 1 default RetailPartner (placeholder brand)
  - 3 GarmentCategories  (tops, bottoms, dresses)
  - 10 Garments          (mixed fit_category: structured, draped, stretch)
  - 2 test Users         (alice@example.com, bob@example.com)

Usage:
    python scripts/seed_garments.py
    # or via init_db.sh

Environment (reads from .env.local or DATABASE_URL):
    DATABASE_URL=postgresql://developer:dev_password_123@localhost:5432/fashion_tech_dev
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Bootstrap Python path
# ---------------------------------------------------------------------------
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))
sys.path.insert(0, str(BACKEND_ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(BACKEND_ROOT / ".env.local", override=False)
load_dotenv(BACKEND_ROOT / ".env.example", override=False)

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.models import (
    Base,
    User,
    GarmentCategory,
    RetailPartner,
    Garment,
    GarmentSize,
)

# ---------------------------------------------------------------------------
# DB connection
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt (cost 12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode(), salt).decode()


def seed_categories(db: Session) -> dict[str, GarmentCategory]:
    """Insert garment categories and return slug → object map."""
    categories_data = [
        {"name": "Tops", "slug": "tops", "description": "Shirts, blouses, and tops", "sort_order": 1},
        {"name": "Bottoms", "slug": "bottoms", "description": "Trousers, jeans, skirts", "sort_order": 2},
        {"name": "Dresses", "slug": "dresses", "description": "Casual and formal dresses", "sort_order": 3},
    ]
    result: dict[str, GarmentCategory] = {}
    for data in categories_data:
        existing = db.query(GarmentCategory).filter_by(slug=data["slug"]).first()
        if existing:
            result[data["slug"]] = existing
            continue
        cat = GarmentCategory(**data)
        db.add(cat)
        db.flush()
        result[data["slug"]] = cat
    return result


def seed_retail_partner(db: Session) -> RetailPartner:
    """Insert a placeholder retail partner."""
    existing = db.query(RetailPartner).filter_by(slug="placeholder-brand").first()
    if existing:
        return existing
    partner = RetailPartner(
        name="Placeholder Brand",
        slug="placeholder-brand",
        integration_type="manual",
        is_active=True,
        contact_email="dev@placeholder-brand.example.com",
    )
    db.add(partner)
    db.flush()
    return partner


def seed_garments(
    db: Session,
    brand: RetailPartner,
    categories: dict[str, GarmentCategory],
) -> list[Garment]:
    """Insert 10 test garments (mixed fit_category)."""

    garments_data = [
        # --- STRUCTURED (3) ---
        {
            "sku": "TOP-STR-001",
            "name": "Tailored Oxford Shirt",
            "garment_type": "shirt",
            "fit_category": "structured",
            "fabric_type": "cotton",
            "fabric_weight_gsm": 140.0,
            "fabric_stretch_percent": 2.0,
            "price_usd": 79.99,
            "description": "Classic structured cotton oxford shirt with a crisp collar.",
            "category_slug": "tops",
            "sizes": [
                {"label": "XS", "order": 1, "chest_min": 82, "chest_max": 86, "waist_min": 68, "waist_max": 72},
                {"label": "S",  "order": 2, "chest_min": 86, "chest_max": 92, "waist_min": 72, "waist_max": 78},
                {"label": "M",  "order": 3, "chest_min": 92, "chest_max": 98, "waist_min": 78, "waist_max": 84},
                {"label": "L",  "order": 4, "chest_min": 98, "chest_max": 106, "waist_min": 84, "waist_max": 92},
                {"label": "XL", "order": 5, "chest_min": 106, "chest_max": 114, "waist_min": 92, "waist_max": 100},
            ],
        },
        {
            "sku": "BOT-STR-001",
            "name": "Slim Fit Chinos",
            "garment_type": "trousers",
            "fit_category": "structured",
            "fabric_type": "cotton-twill",
            "fabric_weight_gsm": 260.0,
            "fabric_stretch_percent": 3.0,
            "price_usd": 89.99,
            "description": "Structured slim-fit chinos in cotton twill.",
            "category_slug": "bottoms",
            "sizes": [
                {"label": "28W/30L", "order": 1, "waist_min": 70, "waist_max": 73, "hips_min": 90, "hips_max": 94},
                {"label": "30W/30L", "order": 2, "waist_min": 74, "waist_max": 77, "hips_min": 94, "hips_max": 98},
                {"label": "32W/30L", "order": 3, "waist_min": 78, "waist_max": 81, "hips_min": 98, "hips_max": 102},
                {"label": "34W/30L", "order": 4, "waist_min": 82, "waist_max": 86, "hips_min": 102, "hips_max": 106},
            ],
        },
        {
            "sku": "DRS-STR-001",
            "name": "Power Sheath Dress",
            "garment_type": "dress",
            "fit_category": "structured",
            "fabric_type": "wool-blend",
            "fabric_weight_gsm": 320.0,
            "fabric_stretch_percent": 5.0,
            "price_usd": 149.99,
            "description": "Structured wool-blend sheath dress for professional settings.",
            "category_slug": "dresses",
            "sizes": [
                {"label": "6",  "order": 1, "chest_min": 82, "chest_max": 86, "waist_min": 64, "waist_max": 68, "hips_min": 88, "hips_max": 92},
                {"label": "8",  "order": 2, "chest_min": 86, "chest_max": 90, "waist_min": 68, "waist_max": 72, "hips_min": 92, "hips_max": 96},
                {"label": "10", "order": 3, "chest_min": 90, "chest_max": 94, "waist_min": 72, "waist_max": 76, "hips_min": 96, "hips_max": 100},
                {"label": "12", "order": 4, "chest_min": 94, "chest_max": 98, "waist_min": 76, "waist_max": 80, "hips_min": 100, "hips_max": 104},
            ],
        },
        # --- DRAPED (4) ---
        {
            "sku": "TOP-DRP-001",
            "name": "Fluid Draped Blouse",
            "garment_type": "blouse",
            "fit_category": "draped",
            "fabric_type": "silk",
            "fabric_weight_gsm": 55.0,
            "fabric_stretch_percent": 0.0,
            "price_usd": 119.99,
            "description": "Lightweight silk blouse with an elegant drape.",
            "category_slug": "tops",
            "sizes": [
                {"label": "XS", "order": 1, "chest_min": 80, "chest_max": 90},
                {"label": "S",  "order": 2, "chest_min": 88, "chest_max": 100},
                {"label": "M",  "order": 3, "chest_min": 96, "chest_max": 110},
                {"label": "L",  "order": 4, "chest_min": 106, "chest_max": 120},
            ],
        },
        {
            "sku": "BOT-DRP-001",
            "name": "Wrap Midi Skirt",
            "garment_type": "skirt",
            "fit_category": "draped",
            "fabric_type": "viscose",
            "fabric_weight_gsm": 120.0,
            "fabric_stretch_percent": 0.0,
            "price_usd": 69.99,
            "description": "Fluid viscose wrap midi skirt with side tie.",
            "category_slug": "bottoms",
            "sizes": [
                {"label": "XS", "order": 1, "waist_min": 60, "waist_max": 68},
                {"label": "S",  "order": 2, "waist_min": 66, "waist_max": 74},
                {"label": "M",  "order": 3, "waist_min": 72, "waist_max": 82},
                {"label": "L",  "order": 4, "waist_min": 80, "waist_max": 92},
            ],
        },
        {
            "sku": "DRS-DRP-001",
            "name": "Cascade Maxi Dress",
            "garment_type": "dress",
            "fit_category": "draped",
            "fabric_type": "chiffon",
            "fabric_weight_gsm": 40.0,
            "fabric_stretch_percent": 0.0,
            "price_usd": 199.99,
            "description": "Flowing chiffon maxi dress with a cascade drape detail.",
            "category_slug": "dresses",
            "sizes": [
                {"label": "XS", "order": 1, "chest_min": 80, "chest_max": 88, "waist_min": 60, "waist_max": 68},
                {"label": "S",  "order": 2, "chest_min": 86, "chest_max": 96, "waist_min": 66, "waist_max": 76},
                {"label": "M",  "order": 3, "chest_min": 94, "chest_max": 104, "waist_min": 74, "waist_max": 84},
                {"label": "L",  "order": 4, "chest_min": 102, "chest_max": 114, "waist_min": 82, "waist_max": 94},
            ],
        },
        {
            "sku": "TOP-DRP-002",
            "name": "Oversized Linen Tunic",
            "garment_type": "shirt",
            "fit_category": "draped",
            "fabric_type": "linen",
            "fabric_weight_gsm": 175.0,
            "fabric_stretch_percent": 1.0,
            "price_usd": 85.00,
            "description": "Relaxed draped linen tunic for warm weather.",
            "category_slug": "tops",
            "sizes": [
                {"label": "S",  "order": 1, "chest_min": 100, "chest_max": 110},
                {"label": "M",  "order": 2, "chest_min": 108, "chest_max": 120},
                {"label": "L",  "order": 3, "chest_min": 116, "chest_max": 130},
                {"label": "XL", "order": 4, "chest_min": 124, "chest_max": 140},
            ],
        },
        # --- STRETCH (3) ---
        {
            "sku": "TOP-STX-001",
            "name": "Performance Fitted Tee",
            "garment_type": "t-shirt",
            "fit_category": "stretch",
            "fabric_type": "polyester-elastane",
            "fabric_weight_gsm": 180.0,
            "fabric_stretch_percent": 35.0,
            "price_usd": 45.00,
            "description": "High-stretch performance tee for sport and casual wear.",
            "category_slug": "tops",
            "sizes": [
                {"label": "XS", "order": 1, "chest_min": 78, "chest_max": 86},
                {"label": "S",  "order": 2, "chest_min": 84, "chest_max": 94},
                {"label": "M",  "order": 3, "chest_min": 92, "chest_max": 102},
                {"label": "L",  "order": 4, "chest_min": 100, "chest_max": 112},
                {"label": "XL", "order": 5, "chest_min": 110, "chest_max": 124},
            ],
        },
        {
            "sku": "BOT-STX-001",
            "name": "High-Waist Yoga Leggings",
            "garment_type": "leggings",
            "fit_category": "stretch",
            "fabric_type": "nylon-elastane",
            "fabric_weight_gsm": 200.0,
            "fabric_stretch_percent": 55.0,
            "price_usd": 75.00,
            "description": "Full-length high-waist leggings with 4-way stretch.",
            "category_slug": "bottoms",
            "sizes": [
                {"label": "XS", "order": 1, "waist_min": 60, "waist_max": 66, "hips_min": 84, "hips_max": 90},
                {"label": "S",  "order": 2, "waist_min": 64, "waist_max": 72, "hips_min": 88, "hips_max": 96},
                {"label": "M",  "order": 3, "waist_min": 70, "waist_max": 80, "hips_min": 94, "hips_max": 104},
                {"label": "L",  "order": 4, "waist_min": 78, "waist_max": 90, "hips_min": 100, "hips_max": 114},
            ],
        },
        {
            "sku": "DRS-STX-001",
            "name": "Bodycon Jersey Dress",
            "garment_type": "dress",
            "fit_category": "stretch",
            "fabric_type": "jersey-elastane",
            "fabric_weight_gsm": 220.0,
            "fabric_stretch_percent": 45.0,
            "price_usd": 55.00,
            "description": "Form-fitting stretch jersey dress for evening wear.",
            "category_slug": "dresses",
            "sizes": [
                {"label": "XS", "order": 1, "chest_min": 76, "chest_max": 84, "waist_min": 56, "waist_max": 64, "hips_min": 82, "hips_max": 90},
                {"label": "S",  "order": 2, "chest_min": 82, "chest_max": 92, "waist_min": 62, "waist_max": 72, "hips_min": 88, "hips_max": 98},
                {"label": "M",  "order": 3, "chest_min": 90, "chest_max": 100, "waist_min": 70, "waist_max": 80, "hips_min": 96, "hips_max": 106},
                {"label": "L",  "order": 4, "chest_min": 98, "chest_max": 110, "waist_min": 78, "waist_max": 90, "hips_min": 104, "hips_max": 116},
            ],
        },
    ]

    inserted: list[Garment] = []
    for data in garments_data:
        existing = db.query(Garment).filter_by(sku=data["sku"]).first()
        if existing:
            print(f"  [skip] garment already exists: {data['sku']}")
            inserted.append(existing)
            continue

        sizes_spec = data.pop("sizes")
        category_slug = data.pop("category_slug")

        garment = Garment(
            brand_id=brand.id,
            category_id=categories[category_slug].id,
            model_file_key=f"garments/placeholder-brand/{data['sku']}/model.glb",
            texture_urls={
                "diffuse": f"garments/placeholder-brand/{data['sku']}/diffuse.png"
            },
            **data,
        )
        db.add(garment)
        db.flush()

        for s in sizes_spec:
            size = GarmentSize(
                garment_id=garment.id,
                size_label=s["label"],
                size_order=s["order"],
                chest_min_cm=s.get("chest_min"),
                chest_max_cm=s.get("chest_max"),
                waist_min_cm=s.get("waist_min"),
                waist_max_cm=s.get("waist_max"),
                hips_min_cm=s.get("hips_min"),
                hips_max_cm=s.get("hips_max"),
            )
            db.add(size)

        inserted.append(garment)
        print(f"  [ok]   garment inserted: {garment.sku} ({garment.fit_category})")

    return inserted


def seed_users(db: Session) -> list[User]:
    """Insert 2 test users."""
    users_data = [
        {
            "email": "alice@example.com",
            "password": "AlicePass123!",
            "first_name": "Alice",
            "last_name": "Testuser",
            "gender": "female",
            "height_cm": 168,
            "preferred_fit": "normal",
        },
        {
            "email": "bob@example.com",
            "password": "BobPass123!",
            "first_name": "Bob",
            "last_name": "Testuser",
            "gender": "male",
            "height_cm": 180,
            "preferred_fit": "loose",
        },
    ]
    inserted: list[User] = []
    for data in users_data:
        existing = db.query(User).filter_by(email=data["email"]).first()
        if existing:
            print(f"  [skip] user already exists: {data['email']}")
            inserted.append(existing)
            continue
        password = data.pop("password")
        user = User(password_hash=_hash_password(password), **data)
        db.add(user)
        db.flush()
        inserted.append(user)
        print(f"  [ok]   user inserted: {user.email}")
    return inserted


def main() -> None:
    """Run all seed operations inside a single transaction."""
    print("=== Fashion Tech Seed Script ===")
    print(f"Database: {DATABASE_URL.split('@')[-1]}")  # hide credentials

    with SessionLocal() as db:
        try:
            print("\n--- Categories ---")
            categories = seed_categories(db)

            print("\n--- Retail Partner ---")
            brand = seed_retail_partner(db)
            print(f"  partner: {brand.name} ({brand.slug})")

            print("\n--- Garments (10) ---")
            garments = seed_garments(db, brand, categories)

            print("\n--- Users (2) ---")
            users = seed_users(db)

            db.commit()

            print(f"\n✅ Done — {len(garments)} garments, {len(users)} users seeded.")
        except Exception as exc:
            db.rollback()
            print(f"\n❌ Seed failed: {exc}")
            raise


if __name__ == "__main__":
    main()
