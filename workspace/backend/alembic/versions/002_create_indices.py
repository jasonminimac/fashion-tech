"""Add performance indexes on hot-query columns.

Revision ID: 002
Revises: 001
Create Date: 2026-03-18

Indexes added:
  - users: email (already in 001, kept for reference), deleted_at filter
  - scans: user_id + status composite, deleted_at filter
  - garments: fit_category, fabric_type, deleted_at filter
  - outfit_items: garment_id (already in 001)
  - scan_measurements: scan_id (already in 001)
  - retailer_api_access: (user_id, retail_partner_id) composite
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create additional performance indexes."""

    # Composite index: look up scans by user quickly filtered by status
    op.create_index(
        "idx_scans_user_id_status",
        "scans",
        ["user_id", "status"],
        postgresql_ops={"status": "text_pattern_ops"},
    )

    # Partial index: active (non-deleted) scans per user
    op.create_index(
        "idx_scans_user_id_active",
        "scans",
        ["user_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Garment fit_category — used heavily in recommendation queries
    op.create_index(
        "idx_garments_fit_category",
        "garments",
        ["fit_category"],
    )

    # Garment fabric_type — used in filter queries
    op.create_index(
        "idx_garments_fabric_type",
        "garments",
        ["fabric_type"],
    )

    # Partial index: active (non-deleted) garments
    op.create_index(
        "idx_garments_active",
        "garments",
        ["id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Composite index: active outfits per user sorted by creation date
    op.create_index(
        "idx_outfits_user_id_created_at",
        "outfits",
        ["user_id", "created_at"],
    )

    # Partial index: non-deleted outfits
    op.create_index(
        "idx_outfits_active",
        "outfits",
        ["user_id"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    # Composite unique index: one access record per (user, partner) pair
    op.create_index(
        "idx_retailer_api_access_user_partner",
        "retailer_api_access",
        ["user_id", "retail_partner_id"],
        unique=True,
    )

    # Partial index: active retailer access grants
    op.create_index(
        "idx_retailer_api_access_active",
        "retailer_api_access",
        ["retail_partner_id"],
        postgresql_where=sa.text("is_active = true AND consent_withdrawn_at IS NULL"),
    )


def downgrade() -> None:
    """Drop additional indexes."""
    op.drop_index("idx_retailer_api_access_active", table_name="retailer_api_access")
    op.drop_index("idx_retailer_api_access_user_partner", table_name="retailer_api_access")
    op.drop_index("idx_outfits_active", table_name="outfits")
    op.drop_index("idx_outfits_user_id_created_at", table_name="outfits")
    op.drop_index("idx_garments_active", table_name="garments")
    op.drop_index("idx_garments_fabric_type", table_name="garments")
    op.drop_index("idx_garments_fit_category", table_name="garments")
    op.drop_index("idx_scans_user_id_active", table_name="scans")
    op.drop_index("idx_scans_user_id_status", table_name="scans")
