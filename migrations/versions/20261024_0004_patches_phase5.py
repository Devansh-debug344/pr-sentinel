"""add patches tables

Revision ID: 20261024_0004
Revises: 20261024_0003
Create Date: 2026-10-24 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20261024_0004'
down_revision: Union[str, None] = '20261024_0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('patches',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('investigation_id', sa.Uuid(), nullable=False),
    sa.Column('finding_id', sa.Uuid(), nullable=True),
    sa.Column('repository_id', sa.Uuid(), nullable=False),
    sa.Column('target_commit_sha', sa.String(length=64), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('affected_files', sa.Text(), nullable=True),
    sa.Column('unified_diff', sa.Text(), nullable=True),
    sa.Column('rationale', sa.Text(), nullable=True),
    sa.Column('assumptions', sa.Text(), nullable=True),
    sa.Column('uncertainties', sa.Text(), nullable=True),
    sa.Column('side_effects', sa.Text(), nullable=True),
    sa.Column('review_notes', sa.Text(), nullable=True),
    sa.Column('generation_meta', sa.Text(), nullable=True),
    sa.Column('verification_status', sa.String(length=32), nullable=False),
    sa.Column('verification_summary', sa.Text(), nullable=True),
    sa.Column('human_approval_status', sa.String(length=32), nullable=False),
    sa.Column('approved_by', sa.String(length=255), nullable=True),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('rejected_by', sa.String(length=255), nullable=True),
    sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['finding_id'], ['analysis_findings.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patches_finding_id'), 'patches', ['finding_id'], unique=False)
    op.create_index(op.f('ix_patches_investigation_id'), 'patches', ['investigation_id'], unique=False)
    op.create_index(op.f('ix_patches_repository_id'), 'patches', ['repository_id'], unique=False)
    op.create_index(op.f('ix_patches_status'), 'patches', ['status'], unique=False)
    op.create_index(op.f('ix_patches_target_commit_sha'), 'patches', ['target_commit_sha'], unique=False)
    op.create_table('patch_verifications',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('patch_id', sa.Uuid(), nullable=False),
    sa.Column('check_type', sa.String(length=64), nullable=True),
    sa.Column('tool', sa.String(length=64), nullable=True),
    sa.Column('outcome', sa.String(length=16), nullable=True),
    sa.Column('exit_code', sa.Integer(), nullable=True),
    sa.Column('sanitized_output', sa.Text(), nullable=True),
    sa.Column('duration_ms', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['patch_id'], ['patches.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_patch_verifications_patch_id'), 'patch_verifications', ['patch_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_patch_verifications_patch_id'), table_name='patch_verifications')
    op.drop_table('patch_verifications')
    op.drop_index(op.f('ix_patches_target_commit_sha'), table_name='patches')
    op.drop_index(op.f('ix_patches_status'), table_name='patches')
    op.drop_index(op.f('ix_patches_repository_id'), table_name='patches')
    op.drop_index(op.f('ix_patches_investigation_id'), table_name='patches')
    op.drop_index(op.f('ix_patches_finding_id'), table_name='patches')
    op.drop_table('patches')
