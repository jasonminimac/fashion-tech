#!/usr/bin/env python3
"""
Seed script — Week 2 Production Data.

Creates:
  1. Founder account (Seb) — test user for end-to-end validation
  2. 5 MVP garments across categories (shirt, trousers, dress, jacket, jeans)
  3. 2 garment categories (tops, bottoms)
  4. Placeholder retail partner for seeded garments

Usage:
    python scripts/seed_production.py
    python scripts/seed_production.py --founder-only
    python scripts/seed_production.py --garments-only
    python scripts/seed_production.py --reset   # drops existing seed data first

Environment:
    DATABASE_URL — postgres connection string (default: from .env)
"""

import argparse
import os
import sys
import uuid
from datetime import datetime

# Ensure src/ is on path when run from backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from src.app.database.engine import SessionLocal, engine
from src.app.models.base import Base
from src.app.models.user import User
from src.app.models.garment import Garment, GarmentSize, GarmentCategory, RetailPartner
from src.app.utils.security import hash_password


# ─── Seed constants ───────────────────────────────────────────────────────────

FOUNDER_EMAIL = "seb@fashiontech.com"
FOUNDER_PASSWORD = "FounderTest2026!"  # local dev only — NOT production

# Fixed UUIDs for reproducibility (so seeds are idempotent)
FOUNDER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
RETAIL_PARTNER_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")
CAT_TOPS_ID = uuid.UUID("00000000-0000-0000-0000-000000000020")
CAT_BOTTOMS_ID = uuid.UUID("00000000-0000-0000-0000-000000000021")
CAT_OUTERWEAR_ID = uuid.UUID("00000000-0000-0000-0000-000000000022")
CAT_DRESSES_ID = uuid.UUID("00000000-0000-0000-0000-000000000023")

MVP_GARMENTS = [
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000001"),
        "sku": "MVPTOP-001",
        "name": "Classic White Oxford Shirt",
        "description": "Tailored Oxford shirt in premium cotton poplin. Regular fit.",
        "garment_type": "shirt",
        "category_id": CAT_TOPS_ID,
        "fit_category": "regular",
        "fabric_type": "cotton_poplin",
        "fabric_weight_gsm": 120.0,
        "fabric_stretch_percent": 2.0,
        "price_usd": 89.00,
        "model_file_key": "garments/mvp/shirts/oxford_white.glb",
        "texture_urls": {
            "diffuse": "garments/mvp/shirts/oxford_white_diffuse.png",
            "normal": "garments/mvp/shirts/oxford_white_normal.png",
        },
        "sizes": [
            {"label": "S", "order": 1, "chest": (86, 91), "waist": (71, 76), "hips": (91, 96)},
            {"label": "M", "order": 2, "chest": (91, 96), "waist": (76, 81), "hips": (96, 101)},
            {"label": "L", "order": 3, "chest": (96, 101), "waist": (81, 86), "hips": (101, 106)},
            {"label": "XL", "order": 4, "chest": (101, 106), "waist": (86, 91), "hips": (106, 111)},
        ],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000002"),
        "sku": "MVPBOT-001",
        "name": "Slim Fit Chino Trousers",
        "description": "Modern slim-cut chinos in stretch cotton blend. Versatile everyday wear.",
        "garment_type": "trousers",
        "category_id": CAT_BOTTOMS_ID,
        "fit_category": "slim",
        "fabric_type": "cotton_stretch",
        "fabric_weight_gsm": 200.0,
        "fabric_stretch_percent": 8.0,
        "price_usd": 119.00,
        "model_file_key": "garments/mvp/trousers/chino_slim.glb",
        "texture_urls": {
            "diffuse": "garments/mvp/trousers/chino_slim_diffuse.png",
        },
        "sizes": [
            {"label": "28/30", "order": 1, "chest": None, "waist": (71, 73), "hips": (91, 94)},
            {"label": "30/30", "order": 2, "chest": None, "waist": (76, 78), "hips": (96, 99)},
            {"label": "32/32", "order": 3, "chest": None, "waist": (81, 83), "hips": (101, 104)},
            {"label": "34/32", "order": 4, "chest": None, "waist": (86, 88), "hips": (106, 109)},
        ],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000003"),
        "sku": "MVPDRS-001",
        "name": "Wrap Midi Dress",
        "description": "Flattering wrap-style midi dress in lightweight crepe. Occasion wear.",
        "garment_type": "dress",
        "category_id": CAT_DRESSES_ID,
        "fit_category": "relaxed",
        "fabric_type": "crepe_polyester",
        "fabric_weight_gsm": 90.0,
        "fabric_stretch_percent": 5.0,
        "price_usd": 145.00,
        "model_file_key": "garments/mvp/dresses/wrap_midi.glb",
        "texture_urls": {
            "diffuse": "garments/mvp/dresses/wrap_midi_diffuse.png",
        },
        "sizes": [
            {"label": "UK 8", "order": 1, "chest": (81, 83), "waist": (61, 63), "hips": (86, 88)},
            {"label": "UK 10", "order": 2, "chest": (84, 86), "waist": (64, 66), "hips": (89, 91)},
            {"label": "UK 12", "order": 3, "chest": (87, 91), "waist": (67, 71), "hips": (92, 96)},
            {"label": "UK 14", "order": 4, "chest": (92, 96), "waist": (72, 76), "hips": (97, 101)},
        ],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000004"),
        "sku": "MVPOUT-001",
        "name": "Unstructured Blazer",
        "description": "Italian-cut unstructured blazer in wool-linen blend. Business casual.",
        "garment_type": "jacket",
        "category_id": CAT_OUTERWEAR_ID,
        "fit_category": "regular",
        "fabric_type": "wool_linen",
        "fabric_weight_gsm": 280.0,
        "fabric_stretch_percent": 1.0,
        "price_usd": 299.00,
        "model_file_key": "garments/mvp/jackets/blazer_unstructured.glb",
        "texture_urls": {
            "diffuse": "garments/mvp/jackets/blazer_unstructured_diffuse.png",
        },
        "sizes": [
            {"label": "36R", "order": 1, "chest": (91, 94), "waist": (76, 79), "hips": None},
            {"label": "38R", "order": 2, "chest": (94, 97), "waist": (79, 82), "hips": None},
            {"label": "40R", "order": 3, "chest": (97, 100), "waist": (82, 85), "hips": None},
            {"label": "42R", "order": 4, "chest": (100, 103), "waist": (85, 88), "hips": None},
        ],
    },
    {
        "id": uuid.UUID("00000000-0000-0000-0001-000000000005"),
        "sku": "MVPBOT-002",
        "name": "Slim Straight Jeans",
        "description": "Classic slim-straight denim in 12oz selvedge. Essential wardrobe staple.",
        "garment_type": "jeans",
        "category_id": CAT_BOTTOMS_ID,
        "fit_category": "slim",
        "fabric_type": "denim_selvedge",
        "fabric_weight_gsm": 340.0,
        "fabric_stretch_percent": 1.5,
        "price_usd": 149.00,
        "model_file_key": "garments/mvp/jeans/slim_straight_indigo.glb",
        "texture_urls": {
            "diffuse": "garments/mvp/jeans/slim_straight_diffuse.png",
            "normal": "garments/mvp/jeans/slim_straight_normal.png",
        },
        "sizes": [
            {"label": "28/30", "order": 1, "chest": None, "waist": (71, 73), "hips": (91, 94)},
            {"label": "30/30", "order": 2, "chest": None, "waist": (76, 78), "hips": (96, 99)},
            {"label": "32/32", "order": 3, "chest": None, "waist": (81, 83), "hips": (101, 104)},
            {"label": "34/32", "order": 4, "chest": None, "waist": (86, 88), "hips": (106, 109)},
        ],
    },
]

GARMENT_CATEGORIES = [
    {
        "id": CAT_TOPS_ID,
        "name": "Tops",
        "slug": "tops",
        "description": "Shirts, t-shirts, blouses, and knitwear",
        "sort_order": 1,
    },
    {
        "id": CAT_BOTTOMS_ID,
        "name": "Bottoms",
        "slug": "bottoms",
        "description": "Trousers, jeans, shorts, and skirts",
        "sort_order": 2,
    },
    {
        "id": CAT_OUTERWEAR_ID,
        "name": "Outerwear",
        "slug": "outerwear",
        "description": "Jackets, coats, and blazers",
        "sort_order": 3,
    },
    {
        "id": CAT_DRESSES_ID,
        "name": "Dresses",
        "slug": "dresses",
        "description": "Midi, maxi, and mini dresses",
        "sort_order": 4,
    },
]


# ─── Seeding functions ────────────────────────────────────────────────────────

def seed_founder(db, reset: bool = False) -> None:
    existing = db.query(User).filter(User.email == FOUNDER_EMAIL).first()
    if existing:
        if reset:
            db.delete(existing)
            db.commit()
            print(f"  ↳ Deleted existing founder account: {FOUNDER_EMAIL}")
        else:
            print(f"  ✓ Founder already exists: {FOUNDER_EMAIL} (skip)")
            return

    founder = User(
        id=FOUNDER_ID,
        email=FOUNDER_EMAIL,
        first_name="Seb",
        last_name="Founder",
        hashed_password=hash_password(FOUNDER_PASSWORD),
        role="admin",
        is_active=True,
        is_verified=True,
    )
    db.add(founder)
    db.commit()
    print(f"  ✓ Created founder: {FOUNDER_EMAIL} (id={FOUNDER_ID})")
    print(f"    Password: {FOUNDER_PASSWORD}  ← dev only, do NOT use in prod")


def seed_retail_partner(db, reset: bool = False) -> None:
    from src.app.models.garment import RetailPartner
    existing = db.query(RetailPartner).filter(RetailPartner.id == RETAIL_PARTNER_ID).first()
    if existing:
        if reset:
            db.delete(existing)
            db.commit()
        else:
            print("  ✓ Retail partner already exists (skip)")
            return

    partner = RetailPartner(
        id=RETAIL_PARTNER_ID,
        name="Fashion Tech MVP",
        slug="fashion-tech-mvp",
        contact_email="dev@fashiontech.com",
        integration_type="internal",
        is_active=True,
    )
    db.add(partner)
    db.commit()
    print(f"  ✓ Created retail partner: {partner.name} (id={RETAIL_PARTNER_ID})")


def seed_categories(db, reset: bool = False) -> None:
    for cat_data in GARMENT_CATEGORIES:
        existing = db.query(GarmentCategory).filter(GarmentCategory.id == cat_data["id"]).first()
        if existing:
            if reset:
                db.delete(existing)
                db.commit()
            else:
                print(f"  ✓ Category '{cat_data['slug']}' exists (skip)")
                continue

        cat = GarmentCategory(
            id=cat_data["id"],
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data["description"],
            sort_order=cat_data["sort_order"],
        )
        db.add(cat)
        db.commit()
        print(f"  ✓ Created category: {cat.name}")


def seed_garments(db, reset: bool = False) -> None:
    for g_data in MVP_GARMENTS:
        existing = db.query(Garment).filter(Garment.id == g_data["id"]).first()
        if existing:
            if reset:
                db.delete(existing)
                db.commit()
            else:
                print(f"  ✓ Garment '{g_data['sku']}' exists (skip)")
                continue

        garment = Garment(
            id=g_data["id"],
            sku=g_data["sku"],
            name=g_data["name"],
            description=g_data["description"],
            garment_type=g_data["garment_type"],
            category_id=g_data["category_id"],
            brand_id=RETAIL_PARTNER_ID,
            fit_category=g_data["fit_category"],
            fabric_type=g_data["fabric_type"],
            fabric_weight_gsm=g_data["fabric_weight_gsm"],
            fabric_stretch_percent=g_data["fabric_stretch_percent"],
            price_usd=g_data["price_usd"],
            model_file_key=g_data["model_file_key"],
            texture_urls=g_data["texture_urls"],
        )
        db.add(garment)
        db.flush()

        for size_data in g_data["sizes"]:
            chest = size_data.get("chest")
            waist = size_data.get("waist")
            hips = size_data.get("hips")
            size = GarmentSize(
                garment_id=garment.id,
                size_label=size_data["label"],
                size_order=size_data["order"],
                chest_min_cm=chest[0] if chest else None,
                chest_max_cm=chest[1] if chest else None,
                waist_min_cm=waist[0] if waist else None,
                waist_max_cm=waist[1] if waist else None,
                hips_min_cm=hips[0] if hips else None,
                hips_max_cm=hips[1] if hips else None,
            )
            db.add(size)

        db.commit()
        print(f"  ✓ Created garment: {garment.name} ({len(g_data['sizes'])} sizes)")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Seed Week 2 production data")
    parser.add_argument("--founder-only", action="store_true", help="Only seed founder account")
    parser.add_argument("--garments-only", action="store_true", help="Only seed garments")
    parser.add_argument("--reset", action="store_true", help="Drop and re-create seed data")
    args = parser.parse_args()

    print("🌱 Fashion Tech — Week 2 Seed Script")
    print(f"   Database: {os.environ.get('DATABASE_URL', '(from .env)')}")
    print()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.founder_only:
            print("👤 Seeding founder account...")
            seed_founder(db, reset=args.reset)
        elif args.garments_only:
            print("👔 Seeding garments...")
            seed_retail_partner(db, reset=args.reset)
            seed_categories(db, reset=args.reset)
            seed_garments(db, reset=args.reset)
        else:
            print("👤 Seeding founder account...")
            seed_founder(db, reset=args.reset)
            print()
            print("🏪 Seeding retail partner...")
            seed_retail_partner(db, reset=args.reset)
            print()
            print("🗂  Seeding garment categories...")
            seed_categories(db, reset=args.reset)
            print()
            print("👔 Seeding MVP garments...")
            seed_garments(db, reset=args.reset)

        print()
        print("✅ Seed complete.")
        print()
        print("Quick test:")
        print(f"  Founder login: POST /v1/auth/login")
        print(f"  Email:    {FOUNDER_EMAIL}")
        print(f"  Password: {FOUNDER_PASSWORD}")

    except Exception as e:
        print(f"❌ Seed failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
