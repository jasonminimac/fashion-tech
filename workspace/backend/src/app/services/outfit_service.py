"""
Outfit Service — CRUD operations for outfits.

All functions accept a SQLAlchemy ``db`` session.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.models.outfit import Outfit, OutfitItem
from app.utils.errors import NotFoundError, PermissionError, OutfitError, ValidationError

logger = logging.getLogger(__name__)


# ─── Create ──────────────────────────────────────────────────────────────────

def create_outfit(
    db: Session,
    user_id: str,
    name: str,
    garment_ids: list[str],
    scan_id: Optional[str] = None,
    description: Optional[str] = None,
) -> Outfit:
    """Create a new outfit for a user, attaching the given garments.

    Args:
        db:          SQLAlchemy session.
        user_id:     UUID string of the owning user.
        name:        Display name for the outfit.
        garment_ids: Ordered list of garment UUID strings.
        scan_id:     (optional) UUID string of associated body scan.
        description: (optional) Free-text description.

    Returns:
        Newly created and committed Outfit ORM object (with items loaded).

    Raises:
        ValidationError: If name is empty or garment_ids is empty.

    Example:
        outfit = create_outfit(db, user_id="u1", name="Summer look",
                               garment_ids=["g1", "g2"])
    """
    name = (name or "").strip()
    if not name:
        raise ValidationError("Outfit name must not be empty")
    if not garment_ids:
        raise ValidationError("Outfit must contain at least one garment")

    outfit = Outfit(
        user_id=user_id,
        name=name,
        description=description,
        scan_id=scan_id,
    )
    db.add(outfit)
    db.flush()  # Get outfit.id before creating items

    for order, garment_id in enumerate(garment_ids):
        item = OutfitItem(
            outfit_id=outfit.id,
            garment_id=garment_id,
            display_order=order,
        )
        db.add(item)

    db.commit()
    db.refresh(outfit)
    logger.info("Created outfit %s for user %s with %d garments", outfit.id, user_id, len(garment_ids))
    return outfit


# ─── List ────────────────────────────────────────────────────────────────────

def list_outfits(
    db: Session,
    user_id: str,
    include_deleted: bool = False,
) -> list[Outfit]:
    """Return all outfits belonging to a user.

    Args:
        db:              SQLAlchemy session.
        user_id:         UUID string of the user.
        include_deleted: If True, include soft-deleted outfits.

    Returns:
        List of Outfit ORM objects, ordered newest-first.

    Example:
        outfits = list_outfits(db, user_id="u1")
    """
    query = db.query(Outfit).filter(Outfit.user_id == user_id)
    if not include_deleted:
        query = query.filter(Outfit.deleted_at.is_(None))
    results = query.order_by(Outfit.created_at.desc()).all()
    logger.debug("list_outfits(user=%s) → %d outfits", user_id, len(results))
    return results


# ─── Update ──────────────────────────────────────────────────────────────────

def update_outfit(
    db: Session,
    outfit_id: str,
    user_id: str,
    data: dict[str, Any],
) -> Outfit:
    """Update an outfit's metadata and/or garment list.

    Allowed data keys: name, description, is_private, mood, occasions,
    preview_image_url, garment_ids (replaces all items).

    Args:
        db:        SQLAlchemy session.
        outfit_id: UUID string of the outfit to update.
        user_id:   UUID string of the requesting user (ownership check).
        data:      Dict of fields to update.

    Returns:
        Updated and committed Outfit ORM object.

    Raises:
        NotFoundError:  If the outfit does not exist or is deleted.
        PermissionError: If user_id does not own the outfit.

    Example:
        updated = update_outfit(db, outfit_id="o1", user_id="u1",
                                data={"name": "New name"})
    """
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.deleted_at.is_(None))
        .first()
    )
    if outfit is None:
        raise NotFoundError(f"Outfit {outfit_id} not found")
    if str(outfit.user_id) != str(user_id):
        raise PermissionError("You do not own this outfit")

    # Scalar field updates
    _scalar_fields = {"name", "description", "is_private", "mood", "occasions", "preview_image_url"}
    for field in _scalar_fields:
        if field in data:
            value = data[field]
            if field == "name":
                value = (value or "").strip()
                if not value:
                    raise ValidationError("Outfit name must not be empty")
            setattr(outfit, field, value)

    # Replace garment items if provided
    if "garment_ids" in data:
        new_ids: list[str] = data["garment_ids"]
        if not new_ids:
            raise ValidationError("Outfit must contain at least one garment")
        # Delete old items
        db.query(OutfitItem).filter(OutfitItem.outfit_id == outfit.id).delete()
        for order, garment_id in enumerate(new_ids):
            db.add(OutfitItem(outfit_id=outfit.id, garment_id=garment_id, display_order=order))

    db.commit()
    db.refresh(outfit)
    logger.info("Updated outfit %s (user=%s)", outfit_id, user_id)
    return outfit


# ─── Soft Delete ─────────────────────────────────────────────────────────────

def delete_outfit(db: Session, outfit_id: str, user_id: str) -> None:
    """Soft-delete an outfit.

    Args:
        db:        SQLAlchemy session.
        outfit_id: UUID string of the outfit.
        user_id:   Requesting user's UUID string (ownership check).

    Raises:
        NotFoundError:  If outfit not found.
        PermissionError: If user doesn't own it.
    """
    outfit = (
        db.query(Outfit)
        .filter(Outfit.id == outfit_id, Outfit.deleted_at.is_(None))
        .first()
    )
    if outfit is None:
        raise NotFoundError(f"Outfit {outfit_id} not found")
    if str(outfit.user_id) != str(user_id):
        raise PermissionError("You do not own this outfit")

    outfit.deleted_at = datetime.now(timezone.utc)
    db.commit()
    logger.info("Soft-deleted outfit %s (user=%s)", outfit_id, user_id)
