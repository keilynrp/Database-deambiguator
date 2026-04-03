"""sprint_106_llm_query_reformulation

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa


revision = "d3e4f5a6b7c8"
down_revision = "c2d3e4f5a6b7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("authority_records") as batch_op:
        batch_op.add_column(sa.Column("reformulation_applied", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("reformulation_gain", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("reformulation_cost_estimate", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("reformulation_trace", sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("authority_records") as batch_op:
        batch_op.drop_column("reformulation_trace")
        batch_op.drop_column("reformulation_cost_estimate")
        batch_op.drop_column("reformulation_gain")
        batch_op.drop_column("reformulation_applied")
