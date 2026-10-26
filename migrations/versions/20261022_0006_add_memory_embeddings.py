"""Add memory embeddings with pgvector support.

Revision ID: 20261022_0006
Revises: 20261022_0005
Create Date: 2026-10-22 01:00:00
"""

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision = "20261022_0006"
down_revision = "20261022_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure pgvector extension is available
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "memory_embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("memory_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column(
            "model", sa.String(length=128), nullable=False, server_default="text-embedding-3-small"
        ),
        sa.Column(
            "model_version",
            sa.String(length=128),
            nullable=False,
            server_default="text-embedding-3-small-2024-02-01",
        ),
        sa.Column("dimensions", sa.Integer(), nullable=False, server_default="1536"),
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
        sa.ForeignKeyConstraint(
            ["memory_id", "user_id"],
            ["memories.id", "memories.user_id"],
            name="fk_memory_embeddings_memory_owner",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_memory_embeddings_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_memory_embeddings"),
        sa.UniqueConstraint("memory_id", name="uq_memory_embeddings_memory_id"),
    )
    op.create_index("ix_memory_embeddings_user_id", "memory_embeddings", ["user_id"], unique=False)
    op.create_index(
        "ix_memory_embeddings_memory_id", "memory_embeddings", ["memory_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_memory_embeddings_user_id", table_name="memory_embeddings")
    op.drop_index("ix_memory_embeddings_memory_id", table_name="memory_embeddings")
    op.drop_table("memory_embeddings")
