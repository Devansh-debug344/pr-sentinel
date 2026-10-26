"""Create user-controlled long-term memory tables.

Revision ID: 20261022_0005
Revises: 20261022_0004
Create Date: 2026-10-22 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "20261022_0005"
down_revision = "20261022_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "memories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=32), server_default="other", nullable=False),
        sa.Column(
            "source",
            sa.String(length=32),
            server_default="user_explicit",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("char_length(content) > 0", name="ck_memories_content_not_empty"),
        sa.CheckConstraint(
            "category IN ('preference', 'goal', 'context', 'routine', 'relationship', 'other')",
            name="ck_memories_valid_category",
        ),
        sa.CheckConstraint("source IN ('user_explicit')", name="ck_memories_valid_source"),
        sa.CheckConstraint(
            "expires_at IS NULL OR expires_at > created_at",
            name="ck_memories_expiry_after_creation",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_memories_user_id_users", ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memories"),
        sa.UniqueConstraint("id", "user_id", name="uq_memories_id_user_id"),
    )
    op.create_index("ix_memories_user_id", "memories", ["user_id"], unique=False)
    op.create_index(
        "ix_memories_user_id_created_at", "memories", ["user_id", "created_at"], unique=False
    )
    op.create_index(
        "ix_memories_user_id_category", "memories", ["user_id", "category"], unique=False
    )

    op.create_table(
        "memory_derivations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("memory_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("external_ref", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "kind IN ('summary', 'embedding', 'cache')", name="ck_memory_derivations_valid_kind"
        ),
        sa.ForeignKeyConstraint(
            ["memory_id", "user_id"],
            ["memories.id", "memories.user_id"],
            name="fk_memory_derivations_memory_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_memory_derivations_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memory_derivations"),
    )
    op.create_index(
        "ix_memory_derivations_memory_id", "memory_derivations", ["memory_id"], unique=False
    )
    op.create_index(
        "ix_memory_derivations_user_id", "memory_derivations", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_memory_derivations_user_id", table_name="memory_derivations")
    op.drop_index("ix_memory_derivations_memory_id", table_name="memory_derivations")
    op.drop_table("memory_derivations")
    op.drop_index("ix_memories_user_id_category", table_name="memories")
    op.drop_index("ix_memories_user_id_created_at", table_name="memories")
    op.drop_index("ix_memories_user_id", table_name="memories")
    op.drop_table("memories")
