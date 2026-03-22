"""add metadata_hash to ingestion jobs

Revision ID: 20260322_02
Revises: 20260322_01
Create Date: 2026-03-22 00:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260322_02"
down_revision = "20260322_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingestion_jobs",
        sa.Column("metadata_hash", sa.String(length=128), nullable=False, server_default=""),
    )
    op.create_index("ix_ingestion_jobs_metadata_hash", "ingestion_jobs", ["metadata_hash"])


def downgrade() -> None:
    op.drop_index("ix_ingestion_jobs_metadata_hash", table_name="ingestion_jobs")
    op.drop_column("ingestion_jobs", "metadata_hash")
