"""Add conversation creation idempotency records.

Revision ID: 20261022_0003
Revises: 20261022_0002
Create Date: 2026-10-22 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "20261022_0003"
down_revision = "20261022_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversation_create_idempotency",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name="fk_conversation_create_idempotency_conversation_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_conversation_create_idempotency_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_conversation_create_idempotency"),
        sa.UniqueConstraint(
            "user_id", "idempotency_key", name="uq_conversation_create_idempotency"
        ),
    )
    op.create_index(
        "ix_conversation_create_idempotency_conversation_id",
        "conversation_create_idempotency",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_conversation_create_idempotency_conversation_id",
        table_name="conversation_create_idempotency",
    )
    op.drop_table("conversation_create_idempotency")
