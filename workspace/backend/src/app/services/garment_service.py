"""
Garment Service — search, size recommendation, and upload validation.

Operates via SQLAlchemy sessions. All DB-touching functions accept an
optional ``db`` session; pass a real session in production, or a mock
session in tests.

Fit recommendation algorithm:
    Compare user's chest_cm (from ScanMeasurement) to each GarmentSize's
    chest_min_cm / chest_max_cm range.  Return the label of the best match.
"""

import logging
import uuid
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.garment import Garment, GarmentSize
from app.utils.errors import ValidationError, NotFoundError, GarmentError

logger = logging.getLogger(__name__)


# ─── Search ──────────────────────────────────────────────────────────────────

def search_garments(
    db: Session,
    *,
    category: Optional[str] = None,
    fit_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Garment]:
    """Search garments with optional category and fit_type filters.

    Args:
        db:        SQLAlchemy session.
        category:  Filter by garment_type (e.g. "shirt", "jeans").
        fit_type:  Filter by fit_category (e.g. "slim", "relaxed").
        limit:     Max results to return (default 20).
        offset:    Pagination offset (default 0).

    Returns:
        List of matching Garment ORM objects.

    Example:
        results = search_garments(db, category="shirt", fit_type="slim", limit=10)
    """
    query = db.query(Garment).filter(Garment.deleted_at.is_(None))

    if category:
        query = query.filter(Garment.garment_type == category)
    if fit_type:
        query = query.filter(Garment.fit_category == fit_type)

    results = query.offset(offset).limit(limit).all()
    logger.debug(
        "search_garments(category=%r, fit_type=%r) → %d results",
        category,
        fit_type,
        len(results),
    )
    return results


# ─── Size Recommendation ─────────────────────────────────────────────────────

def recommend_size(
    db: Session,
    user_scan,  # ScanMeasurement ORM object
    garment_id: str,
) -> str:
    """Recommend a size label for a user based on chest measurement.

    Compares user's chest_cm to each GarmentSize's chest_min_cm / chest_max_cm.
    Returns the label of the first matching range, or the nearest size if
    no range exactly matches.

    Args:
        db:           SQLAlchemy session.
        user_scan:    ScanMeasurement object with chest_cm attribute.
        garment_id:   UUID string of the garment.

    Returns:
        Size label string (e.g. "M", "L", "XL").

    Raises:
        NotFoundError: If garment not found or has no sizes.
        GarmentError:  If user scan has no chest measurement.

    Example:
        size = recommend_size(db, scan_measurement, garment_id="uuid-...")
        # → "M"
    """
    chest_cm: Optional[float] = getattr(user_scan, "chest_cm", None)
    if chest_cm is None:
        raise GarmentError("User scan has no chest_cm measurement")

    sizes: list[GarmentSize] = (
        db.query(GarmentSize)
        .filter(GarmentSize.garment_id == garment_id)
        .order_by(GarmentSize.size_order)
        .all()
    )
    if not sizes:
        raise NotFoundError(f"No sizes found for garment {garment_id}")

    # Try exact range match first
    for size in sizes:
        lo = size.chest_min_cm
        hi = size.chest_max_cm
        if lo is not None and hi is not None:
            if lo <= chest_cm <= hi:
                logger.debug(
                    "recommend_size: chest=%.1f fits %s (%s–%s)",
                    chest_cm,
                    size.size_label,
                    lo,
                    hi,
                )
                return size.size_label

    # Fallback: nearest midpoint
    def midpoint_distance(s: GarmentSize) -> float:
        lo = s.chest_min_cm or 0.0
        hi = s.chest_max_cm or 0.0
        mid = (lo + hi) / 2.0
        return abs(chest_cm - mid)

    nearest = min(sizes, key=midpoint_distance)
    logger.debug(
        "recommend_size fallback: chest=%.1f → nearest size %s",
        chest_cm,
        nearest.size_label,
    )
    return nearest.size_label


# ─── Upload Validation ───────────────────────────────────────────────────────

_REQUIRED_GARMENT_FIELDS = ("name", "garment_type", "model_file_key")


def validate_garment_upload(brand_id: str, garment_data: dict) -> dict:
    """Validate garment data before inserting into the database.

    Args:
        brand_id:     UUID string of the brand (RetailPartner).
        garment_data: Dict of garment fields to validate.

    Returns:
        Validated (and lightly normalised) garment_data dict.

    Raises:
        ValidationError: If required fields are missing or invalid.

    Example:
        validated = validate_garment_upload(
            brand_id="brand-uuid",
            garment_data={"name": "Blue Shirt", "garment_type": "shirt", "model_file_key": "..."},
        )
    """
    if not brand_id:
        raise ValidationError("brand_id is required")

    # Validate required fields
    for field in _REQUIRED_GARMENT_FIELDS:
        if not garment_data.get(field):
            raise ValidationError(f"Missing required field: {field}")

    # Validate model_file_key extension (rudimentary)
    key: str = garment_data["model_file_key"]
    if not key.endswith((".fbx", ".glb", ".gltf", ".obj")):
        raise ValidationError(
            f"model_file_key must point to a supported 3D file (.fbx, .glb, .gltf, .obj), got: {key!r}"
        )

    # Validate price if present
    price = garment_data.get("price_usd")
    if price is not None:
        try:
            price_f = float(price)
            if price_f < 0:
                raise ValidationError("price_usd must be non-negative")
            garment_data["price_usd"] = price_f
        except (TypeError, ValueError):
            raise ValidationError(f"price_usd must be a number, got {price!r}")

    # Normalise name
    garment_data["name"] = garment_data["name"].strip()

    logger.debug("validate_garment_upload OK: %s (brand=%s)", garment_data["name"], brand_id)
    return garment_data
