"""
Alembic migration: Week 2 - Add scan_job_id + pipeline metadata columns.

Revision: 004_week2_scan_pipeline
Previous: 003_add_constraints
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "004_week2_scan_pipeline"
down_revision = "003_add_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add pipeline metadata columns to scans table
    op.add_column("scans", sa.Column(
        "pipeline_version",
        sa.String(50),
        nullable=True,
        comment="Version of pipeline that processed this scan",
    ))
    op.add_column("scans", sa.Column(
        "processing_started_at",
        sa.DateTime(timezone=True),
        nullable=True,
        comment="When pipeline processing began",
    ))
    op.add_column("scans", sa.Column(
        "processing_completed_at",
        sa.DateTime(timezone=True),
        nullable=True,
        comment="When pipeline processing completed",
    ))
    op.add_column("scans", sa.Column(
        "ply_file_size_bytes",
        sa.BigInteger(),
        nullable=True,
        comment="Raw .ply upload size in bytes",
    ))

    # Add fit_notes to scan_measurements for clothing lead integration
    op.add_column("scan_measurements", sa.Column(
        "fit_profile_notes",
        sa.Text(),
        nullable=True,
        comment="Clothing lead notes on fit profile",
    ))

    # Index for status polling performance
    op.create_index(
        "ix_scans_status_created",
        "scans",
        ["status", "created_at"],
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("ix_scans_status_created", table_name="scans")
    op.drop_column("scan_measurements", "fit_profile_notes")
    op.drop_column("scans", "ply_file_size_bytes")
    op.drop_column("scans", "processing_completed_at")
    op.drop_column("scans", "processing_started_at")
    op.drop_column("scans", "pipeline_version")
