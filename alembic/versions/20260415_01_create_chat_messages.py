"""create chat messages

Revision ID: 20260415_01
Revises: 20260322_02
Create Date: 2026-04-15 00:00:00

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260415_01"
down_revision = "20260322_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("message_id", sa.String(length=64), primary_key=True),
        sa.Column("user_hash", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("model", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("run_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_chat_messages_user_hash", "chat_messages", ["user_hash"])
    op.create_index("ix_chat_messages_status", "chat_messages", ["status"])
    op.create_index("ix_chat_messages_run_id", "chat_messages", ["run_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_run_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_status", table_name="chat_messages")
    op.drop_index("ix_chat_messages_user_hash", table_name="chat_messages")
    op.drop_table("chat_messages")
