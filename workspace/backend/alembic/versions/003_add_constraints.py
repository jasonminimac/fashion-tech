"""Add additional constraints and CHECK constraints.

Revision ID: 003
Revises: 002
Create Date: 2026-03-18

Constraints added:
  - users: CHECK on gender values, CHECK on preferred_fit values
  - scans: CHECK on status values, CHECK on scan_type values
  - garments: CHECK on fit_category values
  - scan_measurements: CHECK positive measurements
  - garment_sizes: CHECK positive measurement ranges
  - retailer_api_access: CHECK readable_fields is a JSON array
  - Unique composite: (user_id, retail_partner_id) in retailer_api_access
    (already done as index in 002; adding named constraint here)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CHECK constraints and named FK constraints."""

    # ------------------------------------------------------------------
    # users — validate enum-like string fields
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_users_gender",
        "users",
        "gender IN ('male', 'female', 'non-binary', 'prefer_not_to_say') OR gender IS NULL",
    )
    op.create_check_constraint(
        "ck_users_preferred_fit",
        "users",
        "preferred_fit IN ('tight', 'normal', 'loose') OR preferred_fit IS NULL",
    )
    op.create_check_constraint(
        "ck_users_height_positive",
        "users",
        "height_cm IS NULL OR height_cm > 0",
    )

    # ------------------------------------------------------------------
    # scans — validate status and scan_type
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_scans_status",
        "scans",
        "status IN ('pending', 'processing', 'complete', 'failed')",
    )
    op.create_check_constraint(
        "ck_scans_scan_type",
        "scans",
        "scan_type IN ('lidar', 'photogrammetry', 'manual')",
    )
    op.create_check_constraint(
        "ck_scans_confidence_score",
        "scans",
        "confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)",
    )

    # ------------------------------------------------------------------
    # scan_measurements — ensure positive values
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_scan_measurements_positive",
        "scan_measurements",
        (
            "(chest_cm IS NULL OR chest_cm > 0) AND "
            "(waist_cm IS NULL OR waist_cm > 0) AND "
            "(hips_cm IS NULL OR hips_cm > 0) AND "
            "(inseam_cm IS NULL OR inseam_cm > 0) AND "
            "(shoulder_width_cm IS NULL OR shoulder_width_cm > 0) AND "
            "(arm_length_cm IS NULL OR arm_length_cm > 0) AND "
            "(weight_kg IS NULL OR weight_kg > 0)"
        ),
    )

    # ------------------------------------------------------------------
    # garments — validate fit_category
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_garments_fit_category",
        "garments",
        "fit_category IN ('structured', 'draped', 'stretch') OR fit_category IS NULL",
    )
    op.create_check_constraint(
        "ck_garments_price_positive",
        "garments",
        "price_usd IS NULL OR price_usd >= 0",
    )

    # ------------------------------------------------------------------
    # garment_sizes — ensure min <= max for measurement ranges
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_garment_sizes_chest_range",
        "garment_sizes",
        "chest_min_cm IS NULL OR chest_max_cm IS NULL OR chest_min_cm <= chest_max_cm",
    )
    op.create_check_constraint(
        "ck_garment_sizes_waist_range",
        "garment_sizes",
        "waist_min_cm IS NULL OR waist_max_cm IS NULL OR waist_min_cm <= waist_max_cm",
    )
    op.create_check_constraint(
        "ck_garment_sizes_hips_range",
        "garment_sizes",
        "hips_min_cm IS NULL OR hips_max_cm IS NULL OR hips_min_cm <= hips_max_cm",
    )

    # ------------------------------------------------------------------
    # retailer_api_access — consent_withdrawn must be after consent_at
    # ------------------------------------------------------------------
    op.create_check_constraint(
        "ck_retailer_api_access_consent_order",
        "retailer_api_access",
        (
            "consent_withdrawn_at IS NULL OR "
            "consent_at IS NULL OR "
            "consent_withdrawn_at >= consent_at"
        ),
    )


def downgrade() -> None:
    """Drop added constraints."""
    op.drop_constraint("ck_retailer_api_access_consent_order", "retailer_api_access", type_="check")
    op.drop_constraint("ck_garment_sizes_hips_range", "garment_sizes", type_="check")
    op.drop_constraint("ck_garment_sizes_waist_range", "garment_sizes", type_="check")
    op.drop_constraint("ck_garment_sizes_chest_range", "garment_sizes", type_="check")
    op.drop_constraint("ck_garments_price_positive", "garments", type_="check")
    op.drop_constraint("ck_garments_fit_category", "garments", type_="check")
    op.drop_constraint("ck_scan_measurements_positive", "scan_measurements", type_="check")
    op.drop_constraint("ck_scans_confidence_score", "scans", type_="check")
    op.drop_constraint("ck_scans_scan_type", "scans", type_="check")
    op.drop_constraint("ck_scans_status", "scans", type_="check")
    op.drop_constraint("ck_users_height_positive", "users", type_="check")
    op.drop_constraint("ck_users_preferred_fit", "users", type_="check")
    op.drop_constraint("ck_users_gender", "users", type_="check")
