"""migrate chat message_id to bigint autoincrement

Revision ID: 20260421_01
Revises: 20260415_01
Create Date: 2026-04-21 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260421_01"
down_revision = "20260415_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_messages_v2",
        sa.Column("message_id", sa.BigInteger(), primary_key=True, autoincrement=True),
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
    op.create_index("ix_chat_messages_v2_user_hash", "chat_messages_v2", ["user_hash"])
    op.create_index("ix_chat_messages_v2_status", "chat_messages_v2", ["status"])
    op.create_index("ix_chat_messages_v2_run_id", "chat_messages_v2", ["run_id"])
    op.create_index("ix_chat_messages_v2_created_at", "chat_messages_v2", ["created_at"])

    op.execute(
        """
        INSERT INTO chat_messages_v2 (
            user_hash, role, content, input_tokens, output_tokens, total_tokens,
            model, status, error_message, run_id, created_at
        )
        SELECT
            user_hash, role, content, input_tokens, output_tokens, total_tokens,
            model, status, error_message, run_id, created_at
        FROM chat_messages
        ORDER BY created_at ASC, message_id ASC
        """
    )

    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_run_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_status", table_name="chat_messages")
    op.drop_index("ix_chat_messages_user_hash", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.rename_table("chat_messages_v2", "chat_messages")
    op.drop_index("ix_chat_messages_v2_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v2_run_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v2_status", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v2_user_hash", table_name="chat_messages")
    op.create_index("ix_chat_messages_user_hash", "chat_messages", ["user_hash"])
    op.create_index("ix_chat_messages_status", "chat_messages", ["status"])
    op.create_index("ix_chat_messages_run_id", "chat_messages", ["run_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])


def downgrade() -> None:
    op.create_table(
        "chat_messages_v1",
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
    op.create_index("ix_chat_messages_v1_user_hash", "chat_messages_v1", ["user_hash"])
    op.create_index("ix_chat_messages_v1_status", "chat_messages_v1", ["status"])
    op.create_index("ix_chat_messages_v1_run_id", "chat_messages_v1", ["run_id"])
    op.create_index("ix_chat_messages_v1_created_at", "chat_messages_v1", ["created_at"])

    op.execute(
        """
        INSERT INTO chat_messages_v1 (
            message_id, user_hash, role, content, input_tokens, output_tokens, total_tokens,
            model, status, error_message, run_id, created_at
        )
        SELECT
            CONCAT('msg_', LPAD(CAST(message_id AS CHAR), 32, '0')),
            user_hash, role, content, input_tokens, output_tokens, total_tokens,
            model, status, error_message, run_id, created_at
        FROM chat_messages
        ORDER BY message_id ASC
        """
    )

    op.drop_index("ix_chat_messages_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_run_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_status", table_name="chat_messages")
    op.drop_index("ix_chat_messages_user_hash", table_name="chat_messages")
    op.drop_table("chat_messages")

    op.rename_table("chat_messages_v1", "chat_messages")
    op.drop_index("ix_chat_messages_v1_created_at", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v1_run_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v1_status", table_name="chat_messages")
    op.drop_index("ix_chat_messages_v1_user_hash", table_name="chat_messages")
    op.create_index("ix_chat_messages_user_hash", "chat_messages", ["user_hash"])
    op.create_index("ix_chat_messages_status", "chat_messages", ["status"])
    op.create_index("ix_chat_messages_run_id", "chat_messages", ["run_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])
