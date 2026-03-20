"""
Retailer models: RetailPartner and RetailerAPIAccess.

RetailPartner is defined in garment.py (it's tightly coupled to garments).
This module adds the RetailerAPIAccess model for B2B data access control.
"""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import BaseModel

__all__ = ["RetailerAPIAccess"]


class RetailerAPIAccess(BaseModel):
    """
    B2B data access control for retail partners.

    Governs which fit profile fields a retail partner can read for a given user.
    Platform owns raw body scans; retailers may only access derived fit profiles
    after explicit user consent (consent_at is set).

    Readable fields are limited to fit profile data (e.g., chest_cm, waist_cm,
    preferred_fit) — NOT raw mesh / scan files.
    """

    __tablename__ = "retailer_api_access"

    # Who gave consent
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Which retail partner receives access
    retail_partner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("retail_partners.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Consent tracking (GDPR / data ownership)
    consent_at = Column(DateTime, nullable=True)  # NULL = not yet consented
    consent_withdrawn_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=False, nullable=False)

    # Allowlist of fit-profile fields the partner may read.
    # Example: ["chest_cm", "waist_cm", "hips_cm", "preferred_fit"]
    # Raw mesh / scan_file_key are NEVER included here.
    readable_fields = Column(
        JSON,
        nullable=False,
        default=lambda: ["chest_cm", "waist_cm", "hips_cm", "preferred_fit"],
    )

    # Optional notes (e.g., which integration triggered this)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", backref="retailer_api_accesses")
    retail_partner = relationship("RetailPartner", backref="api_accesses")

    def __repr__(self) -> str:
        return (
            f"<RetailerAPIAccess(user_id={self.user_id}, "
            f"partner_id={self.retail_partner_id}, "
            f"active={self.is_active})>"
        )

    @property
    def has_active_consent(self) -> bool:
        """Return True if user has given (and not withdrawn) consent."""
        return (
            self.consent_at is not None
            and self.consent_withdrawn_at is None
            and self.is_active
        )
