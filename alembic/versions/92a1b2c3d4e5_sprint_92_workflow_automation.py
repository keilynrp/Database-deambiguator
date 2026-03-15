"""sprint_92_workflow_automation_engine

Revision ID: 92a1b2c3d4e5
Revises: 91c63bdf196c
Create Date: 2026-03-15 16:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '92a1b2c3d4e5'
down_revision: Union[str, Sequence[str], None] = '91c63bdf196c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("workflows"):
        op.create_table(
            'workflows',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('trigger_type', sa.String(50), nullable=False),
            sa.Column('trigger_config', sa.Text, default='{}'),
            sa.Column('conditions', sa.Text, default='[]'),
            sa.Column('actions', sa.Text, default='[]'),
            sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=True),
            sa.Column('last_run_at', sa.DateTime, nullable=True),
            sa.Column('run_count', sa.Integer, default=0),
            sa.Column('last_run_status', sa.String(20), nullable=True),
        )

    if not inspector.has_table("workflow_runs"):
        op.create_table(
            'workflow_runs',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('workflow_id', sa.Integer, sa.ForeignKey('workflows.id'), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, default='running'),
            sa.Column('trigger_data', sa.Text, default='{}'),
            sa.Column('steps_log', sa.Text, default='[]'),
            sa.Column('error', sa.Text, nullable=True),
            sa.Column('started_at', sa.DateTime, nullable=True),
            sa.Column('completed_at', sa.DateTime, nullable=True),
        )


def downgrade() -> None:
    op.drop_table('workflow_runs')
    op.drop_table('workflows')
