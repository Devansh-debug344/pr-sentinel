"""Add idempotency request IDs for user message submissions."""

import sqlalchemy as sa
from alembic import op

revision = "20261022_0004"
down_revision = "20261022_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("request_id", sa.Uuid(), nullable=True))
    op.create_unique_constraint("uq_messages_request_id", "messages", ["request_id"])


def downgrade() -> None:
    op.drop_constraint("uq_messages_request_id", "messages", type_="unique")
    op.drop_column("messages", "request_id")
