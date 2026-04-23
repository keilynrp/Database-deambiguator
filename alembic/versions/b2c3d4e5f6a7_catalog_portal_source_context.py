"""Add source context to catalog portals

Revision ID: b2c3d4e5f6a7
Revises: a7b8c9d0e1f2
Create Date: 2026-04-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2c3d4e5f6a7"
down_revision = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("catalog_portals") as batch_op:
        batch_op.add_column(sa.Column("source_label", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("source_context_json", sa.Text(), nullable=True, server_default="{}"))


def downgrade() -> None:
    with op.batch_alter_table("catalog_portals") as batch_op:
        batch_op.drop_column("source_context_json")
        batch_op.drop_column("source_label")
