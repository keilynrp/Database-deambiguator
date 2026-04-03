"""sprint_106_hierarchical_fallback

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-04-02
"""

from alembic import op
import sqlalchemy as sa


revision = "c2d3e4f5a6b7"
down_revision = "b1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("authority_records") as batch_op:
        batch_op.add_column(sa.Column("hierarchy_distance", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("authority_records") as batch_op:
        batch_op.drop_column("hierarchy_distance")
