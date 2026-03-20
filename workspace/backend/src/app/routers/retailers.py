"""Retailer B2B API routes."""
import uuid
from fastapi import APIRouter, Depends, Query, Header
from sqlalchemy.orm import Session

from src.app.dependencies import get_db
from src.app.models.user import User
from src.app.models.scan import Scan, ScanMeasurement
from src.app.utils.errors import Unauthorized, NotFound, Forbidden

router = APIRouter(prefix="/api/retailers", tags=["retailers"])


def _verify_retailer_api_key(x_api_key: str = Header(...)) -> str:
    """Placeholder: validate retailer API key.
    
    In production, look up key hash in retail_partners table.
    """
    if not x_api_key or len(x_api_key) < 8:
        raise Unauthorized("Invalid API key")
    return x_api_key


@router.get("/{retailer_id}/fit-profile", response_model=dict)
def get_fit_profile(
    retailer_id: uuid.UUID,
    user_id: uuid.UUID = Query(..., description="User ID to retrieve fit profile for"),
    api_key: str = Depends(_verify_retailer_api_key),
    db: Session = Depends(get_db),
):
    """Get a user's fit profile for a retailer integration.

    Requires:
    - Valid X-Api-Key header (retailer auth)
    - User consent (placeholder — extend with consent model)
    """
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None),
        User.is_active == True,
    ).first()
    if not user:
        raise NotFound("User not found")

    # Consent placeholder — assume true for MVP
    # TODO: check ConsentRecord table when built

    # Get latest completed scan
    scan = (
        db.query(Scan)
        .filter(
            Scan.user_id == user_id,
            Scan.status == "complete",
            Scan.deleted_at.is_(None),
        )
        .order_by(Scan.created_at.desc())
        .first()
    )

    if not scan:
        return {
            "status": "success",
            "data": {
                "user_id": str(user_id),
                "fit_profile": None,
                "message": "No completed scan available",
            },
            "error": None,
        }

    measurements = (
        db.query(ScanMeasurement)
        .filter(ScanMeasurement.scan_id == scan.id)
        .first()
    )

    fit_data = {
        "scan_id": str(scan.id),
        "body_shape": scan.body_shape,
        "confidence_score": scan.confidence_score,
        "measurements": {},
    }

    if measurements:
        fit_data["measurements"] = {
            "chest_cm": measurements.chest_cm,
            "waist_cm": measurements.waist_cm,
            "hips_cm": measurements.hips_cm,
            "inseam_cm": measurements.inseam_cm,
            "shoulder_width_cm": measurements.shoulder_width_cm,
        }

    return {
        "status": "success",
        "data": {"user_id": str(user_id), "fit_profile": fit_data},
        "error": None,
    }
