"""add analysis tables

Revision ID: 20261024_0002
Revises: 20261024_0001
Create Date: 2026-10-24 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20261024_0002'
down_revision: Union[str, None] = '20261024_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('analysis_runs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('investigation_id', sa.Uuid(), nullable=False),
    sa.Column('pull_request_id', sa.Uuid(), nullable=True),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('base_sha', sa.String(length=64), nullable=True),
    sa.Column('head_sha', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('provider', sa.String(length=64), nullable=True),
    sa.Column('model', sa.String(length=128), nullable=True),
    sa.Column('files_analyzed', sa.Integer(), nullable=False),
    sa.Column('bytes_analyzed', sa.Integer(), nullable=False),
    sa.Column('findings_count', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_runs_head_sha'), 'analysis_runs', ['head_sha'], unique=False)
    op.create_index(op.f('ix_analysis_runs_investigation_id'), 'analysis_runs', ['investigation_id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_pull_request_id'), 'analysis_runs', ['pull_request_id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_repository_id'), 'analysis_runs', ['repository_id'], unique=False)
    op.create_index(op.f('ix_analysis_runs_status'), 'analysis_runs', ['status'], unique=False)
    op.create_table('analysis_findings',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('analysis_run_id', sa.Uuid(), nullable=False),
    sa.Column('finding_id', sa.String(length=64), nullable=False),
    sa.Column('category', sa.String(length=32), nullable=True),
    sa.Column('severity', sa.String(length=16), nullable=True),
    sa.Column('title', sa.String(length=256), nullable=True),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.Column('evidence', sa.Text(), nullable=True),
    sa.Column('file_path', sa.String(length=1024), nullable=True),
    sa.Column('line_range', sa.String(length=64), nullable=True),
    sa.Column('suggestion', sa.Text(), nullable=True),
    sa.Column('confidence', sa.String(length=16), nullable=True),
    sa.Column('status', sa.String(length=16), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['analysis_run_id'], ['analysis_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_findings_analysis_run_id'), 'analysis_findings', ['analysis_run_id'], unique=False)
    op.create_index(op.f('ix_analysis_findings_finding_id'), 'analysis_findings', ['finding_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_analysis_findings_finding_id'), table_name='analysis_findings')
    op.drop_index(op.f('ix_analysis_findings_analysis_run_id'), table_name='analysis_findings')
    op.drop_table('analysis_findings')
    op.drop_index(op.f('ix_analysis_runs_status'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_repository_id'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_pull_request_id'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_investigation_id'), table_name='analysis_runs')
    op.drop_index(op.f('ix_analysis_runs_head_sha'), table_name='analysis_runs')
    op.drop_table('analysis_runs')
