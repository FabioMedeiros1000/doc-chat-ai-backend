"""add file_path to ingestion jobs

Revision ID: 20260322_01
Revises: 20260321_01
Create Date: 2026-03-22 00:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260322_01"
down_revision = "20260321_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ingestion_jobs",
        sa.Column("file_path", sa.String(length=1024), nullable=False, server_default=""),
    )


def downgrade() -> None:
    op.drop_column("ingestion_jobs", "file_path")
