"""Sprint 104 - add created_by to artifact_templates

Revision ID: 94c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-03-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "94c4d5e6f7a8"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("artifact_templates") as batch_op:
        batch_op.add_column(sa.Column("created_by", sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("artifact_templates") as batch_op:
        batch_op.drop_column("created_by")
