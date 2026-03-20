"""Initial schema — create all 10 core tables.

Revision ID: 001
Revises: 
Create Date: 2026-03-18

Tables created (in dependency order):
  1.  users
  2.  session_tokens
  3.  scans
  4.  scan_measurements
  5.  garment_categories
  6.  retail_partners
  7.  garments
  8.  garment_sizes
  9.  outfits
  10. outfit_items
  11. saved_favourite_garments
  12. retailer_api_access
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID, JSON

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all core tables."""

    # ------------------------------------------------------------------
    # 1. users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("avatar_url", sa.String(500), nullable=True),
        sa.Column("gender", sa.String(50), nullable=True),
        sa.Column("age_range", sa.String(50), nullable=True),
        sa.Column("height_cm", sa.Integer(), nullable=True),
        sa.Column("preferred_fit", sa.String(50), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("receives_marketing", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("idx_users_email", "users", ["email"])
    op.create_index("idx_users_created_at", "users", ["created_at"])

    # ------------------------------------------------------------------
    # 2. session_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "session_tokens",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("token_family", sa.String(255), nullable=False),
        sa.Column("is_revoked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("token_family", name="uq_session_tokens_family"),
    )
    op.create_index("idx_session_tokens_user_id", "session_tokens", ["user_id"])

    # ------------------------------------------------------------------
    # 3. scans
    # ------------------------------------------------------------------
    op.create_table(
        "scans",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), server_default="My Scan", nullable=True),
        sa.Column("scan_type", sa.String(50), nullable=False),
        sa.Column("scan_file_key", sa.String(500), nullable=True),
        sa.Column("rigged_file_key", sa.String(500), nullable=True),
        sa.Column("status", sa.String(50), server_default="pending", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("body_shape", sa.String(100), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_scans_user_id", "scans", ["user_id"])
    op.create_index("idx_scans_status", "scans", ["status"])

    # ------------------------------------------------------------------
    # 4. scan_measurements
    # ------------------------------------------------------------------
    op.create_table(
        "scan_measurements",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("scan_id", UUID(as_uuid=True), nullable=False),
        sa.Column("chest_cm", sa.Float(), nullable=True),
        sa.Column("waist_cm", sa.Float(), nullable=True),
        sa.Column("hips_cm", sa.Float(), nullable=True),
        sa.Column("inseam_cm", sa.Float(), nullable=True),
        sa.Column("shoulder_width_cm", sa.Float(), nullable=True),
        sa.Column("arm_length_cm", sa.Float(), nullable=True),
        sa.Column("torso_length_cm", sa.Float(), nullable=True),
        sa.Column("weight_kg", sa.Float(), nullable=True),
        sa.Column("bmi", sa.Float(), nullable=True),
        sa.Column("fit_profile_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_scan_measurements_scan_id", "scan_measurements", ["scan_id"])

    # ------------------------------------------------------------------
    # 5. garment_categories
    # ------------------------------------------------------------------
    op.create_table(
        "garment_categories",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parent_id", UUID(as_uuid=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["garment_categories.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("slug", name="uq_garment_categories_slug"),
    )
    op.create_index("idx_garment_categories_slug", "garment_categories", ["slug"])

    # ------------------------------------------------------------------
    # 6. retail_partners
    # ------------------------------------------------------------------
    op.create_table(
        "retail_partners",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("api_endpoint", sa.String(500), nullable=True),
        sa.Column("api_key_hash", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("integration_type", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("slug", name="uq_retail_partners_slug"),
    )
    op.create_index("idx_retail_partners_slug", "retail_partners", ["slug"])

    # ------------------------------------------------------------------
    # 7. garments
    # ------------------------------------------------------------------
    op.create_table(
        "garments",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("sku", sa.String(100), nullable=False),
        sa.Column("brand_id", UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", UUID(as_uuid=True), nullable=True),
        sa.Column("garment_type", sa.String(50), nullable=False),
        sa.Column("model_file_key", sa.String(500), nullable=False),
        sa.Column("texture_urls", JSON(), nullable=True),
        sa.Column("fit_category", sa.String(50), nullable=True),
        sa.Column("fabric_type", sa.String(100), nullable=True),
        sa.Column("fabric_weight_gsm", sa.Float(), nullable=True),
        sa.Column("fabric_stretch_percent", sa.Float(), nullable=True),
        sa.Column("price_usd", sa.Float(), nullable=True),
        sa.Column("retail_url", sa.String(500), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["brand_id"], ["retail_partners.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["category_id"], ["garment_categories.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("sku", name="uq_garments_sku"),
    )
    op.create_index("idx_garments_sku", "garments", ["sku"])
    op.create_index("idx_garments_brand_id", "garments", ["brand_id"])
    op.create_index("idx_garments_category_id", "garments", ["category_id"])

    # ------------------------------------------------------------------
    # 8. garment_sizes
    # ------------------------------------------------------------------
    op.create_table(
        "garment_sizes",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("garment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("size_label", sa.String(50), nullable=False),
        sa.Column("size_order", sa.Integer(), nullable=True),
        sa.Column("chest_min_cm", sa.Float(), nullable=True),
        sa.Column("chest_max_cm", sa.Float(), nullable=True),
        sa.Column("waist_min_cm", sa.Float(), nullable=True),
        sa.Column("waist_max_cm", sa.Float(), nullable=True),
        sa.Column("hips_min_cm", sa.Float(), nullable=True),
        sa.Column("hips_max_cm", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["garment_id"], ["garments.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_garment_sizes_garment_id", "garment_sizes", ["garment_id"])

    # ------------------------------------------------------------------
    # 9. outfits
    # ------------------------------------------------------------------
    op.create_table(
        "outfits",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("scan_id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_private", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("occasions", sa.String(500), nullable=True),
        sa.Column("mood", sa.String(100), nullable=True),
        sa.Column("preview_image_url", sa.String(500), nullable=True),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["scan_id"], ["scans.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_outfits_user_id", "outfits", ["user_id"])
    op.create_index("idx_outfits_scan_id", "outfits", ["scan_id"])

    # ------------------------------------------------------------------
    # 10. outfit_items
    # ------------------------------------------------------------------
    op.create_table(
        "outfit_items",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("outfit_id", UUID(as_uuid=True), nullable=False),
        sa.Column("garment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("garment_size_id", UUID(as_uuid=True), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["outfit_id"], ["outfits.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["garment_id"], ["garments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["garment_size_id"], ["garment_sizes.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("idx_outfit_items_outfit_id", "outfit_items", ["outfit_id"])
    op.create_index("idx_outfit_items_garment_id", "outfit_items", ["garment_id"])

    # ------------------------------------------------------------------
    # 11. saved_favourite_garments
    # ------------------------------------------------------------------
    op.create_table(
        "saved_favourite_garments",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("garment_id", UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["garment_id"], ["garments.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "user_id", "garment_id", name="uq_saved_favourite_user_garment"
        ),
    )
    op.create_index(
        "idx_saved_favourite_garments_user_id", "saved_favourite_garments", ["user_id"]
    )

    # ------------------------------------------------------------------
    # 12. retailer_api_access
    # ------------------------------------------------------------------
    op.create_table(
        "retailer_api_access",
        sa.Column(
            "id",
            UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("retail_partner_id", UUID(as_uuid=True), nullable=False),
        sa.Column("consent_at", sa.DateTime(), nullable=True),
        sa.Column("consent_withdrawn_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("readable_fields", JSON(), nullable=False,
                  server_default='["chest_cm","waist_cm","hips_cm","preferred_fit"]'),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["retail_partner_id"], ["retail_partners.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("idx_retailer_api_access_user_id", "retailer_api_access", ["user_id"])
    op.create_index(
        "idx_retailer_api_access_partner_id",
        "retailer_api_access",
        ["retail_partner_id"],
    )


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""
    op.drop_table("retailer_api_access")
    op.drop_table("saved_favourite_garments")
    op.drop_table("outfit_items")
    op.drop_table("outfits")
    op.drop_table("garment_sizes")
    op.drop_table("garments")
    op.drop_table("retail_partners")
    op.drop_table("garment_categories")
    op.drop_table("scan_measurements")
    op.drop_table("scans")
    op.drop_table("session_tokens")
    op.drop_table("users")
