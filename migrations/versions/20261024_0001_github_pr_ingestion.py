"""add github pr ingestion tables

Revision ID: 20261024_0001
Revises: 
Create Date: 2026-10-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20261024_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('repositories',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('github_id', sa.BigInteger(), nullable=False),
    sa.Column('owner', sa.String(length=255), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('full_name', sa.String(length=512), nullable=False),
    sa.Column('default_branch', sa.String(length=255), nullable=True),
    sa.Column('is_private', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('full_name', name='uq_repositories_full_name'),
    sa.UniqueConstraint('github_id', name='uq_repositories_github_id')
    )
    op.create_index('ix_repositories_owner_name', 'repositories', ['owner', 'name'], unique=False)
    op.create_table('pull_requests',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('github_id', sa.BigInteger(), nullable=True),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=1024), nullable=False),
    sa.Column('state', sa.String(length=32), nullable=False),
    sa.Column('author_login', sa.String(length=255), nullable=True),
    sa.Column('base_branch', sa.String(length=255), nullable=True),
    sa.Column('head_branch', sa.String(length=255), nullable=True),
    sa.Column('base_sha', sa.String(length=64), nullable=True),
    sa.Column('head_sha', sa.String(length=64), nullable=False),
    sa.Column('url', sa.String(length=1024), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('github_id', name='uq_pull_requests_github_id'),
    sa.UniqueConstraint('repository_id', 'number', name='uq_pull_requests_repo_number')
    )
    op.create_index('ix_pull_requests_head_sha', 'pull_requests', ['head_sha'], unique=False)
    op.create_index('ix_pull_requests_repository_id', 'pull_requests', ['repository_id'], unique=False)
    op.create_table('webhook_deliveries',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('delivery_id', sa.String(length=128), nullable=False),
    sa.Column('event_type', sa.String(length=64), nullable=False),
    sa.Column('repository_github_id', sa.BigInteger(), nullable=True),
    sa.Column('repository_full_name', sa.String(length=512), nullable=True),
    sa.Column('pull_request_number', sa.Integer(), nullable=True),
    sa.Column('pull_request_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('delivery_id', name='uq_webhook_deliveries_delivery_id')
    )
    op.create_index('ix_webhook_deliveries_event_type', 'webhook_deliveries', ['event_type'], unique=False)
    op.create_index('ix_webhook_deliveries_received_at', 'webhook_deliveries', ['received_at'], unique=False)
    op.create_index('ix_webhook_deliveries_status', 'webhook_deliveries', ['status'], unique=False)
    op.create_table('investigations',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('pull_request_id', sa.Uuid(), nullable=True),
    sa.Column('trigger', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('target_head_sha', sa.String(length=64), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_investigations_pull_request_id', 'investigations', ['pull_request_id'], unique=False)
    op.create_index('ix_investigations_repository_id', 'investigations', ['repository_id'], unique=False)
    op.create_index('ix_investigations_status', 'investigations', ['status'], unique=False)
    op.create_index('ix_investigations_target_head_sha', 'investigations', ['target_head_sha'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_investigations_target_head_sha', table_name='investigations')
    op.drop_index('ix_investigations_status', table_name='investigations')
    op.drop_index('ix_investigations_repository_id', table_name='investigations')
    op.drop_index('ix_investigations_pull_request_id', table_name='investigations')
    op.drop_table('investigations')
    op.drop_index('ix_webhook_deliveries_status', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_received_at', table_name='webhook_deliveries')
    op.drop_index('ix_webhook_deliveries_event_type', table_name='webhook_deliveries')
    op.drop_table('webhook_deliveries')
    op.drop_index('ix_pull_requests_repository_id', table_name='pull_requests')
    op.drop_index('ix_pull_requests_head_sha', table_name='pull_requests')
    op.drop_table('pull_requests')
    op.drop_index('ix_repositories_owner_name', table_name='repositories')
    op.drop_table('repositories')
