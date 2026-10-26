"""add multiagent workflow tables

Revision ID: 20261024_0003
Revises: 20261024_0002
Create Date: 2026-10-24 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20261024_0003'
down_revision: Union[str, None] = '20261024_0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('workflow_runs',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('investigation_id', sa.Uuid(), nullable=False),
    sa.Column('workflow_type', sa.String(length=64), nullable=False),
    sa.Column('workflow_version', sa.String(length=32), nullable=False),
    sa.Column('state', sa.String(length=32), nullable=False),
    sa.Column('target_head_sha', sa.String(length=64), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['investigation_id'], ['investigations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_runs_investigation_id'), 'workflow_runs', ['investigation_id'], unique=False)
    op.create_index(op.f('ix_workflow_runs_state'), 'workflow_runs', ['state'], unique=False)
    op.create_table('agent_executions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('workflow_run_id', sa.Uuid(), nullable=False),
    sa.Column('agent_type', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=32), nullable=False),
    sa.Column('attempt', sa.Integer(), nullable=False),
    sa.Column('input_refs', sa.Text(), nullable=True),
    sa.Column('output_refs', sa.Text(), nullable=True),
    sa.Column('tool_calls', sa.Integer(), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('error_summary', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['workflow_run_id'], ['workflow_runs.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_executions_agent_type'), 'agent_executions', ['agent_type'], unique=False)
    op.create_index(op.f('ix_agent_executions_status'), 'agent_executions', ['status'], unique=False)
    op.create_index(op.f('ix_agent_executions_workflow_run_id'), 'agent_executions', ['workflow_run_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_agent_executions_workflow_run_id'), table_name='agent_executions')
    op.drop_index(op.f('ix_agent_executions_status'), table_name='agent_executions')
    op.drop_index(op.f('ix_agent_executions_agent_type'), table_name='agent_executions')
    op.drop_table('agent_executions')
    op.drop_index(op.f('ix_workflow_runs_state'), table_name='workflow_runs')
    op.drop_index(op.f('ix_workflow_runs_investigation_id'), table_name='workflow_runs')
    op.drop_table('workflow_runs')
