"""Sprint 106 nil detection layer

Revision ID: b1c2d3e4f5a6
Revises: a2b3c4d5e6f7
Create Date: 2026-04-02 13:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "b1c2d3e4f5a6"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("authority_records", sa.Column("nil_score", sa.Float(), nullable=True))
    op.create_index(op.f("ix_authority_records_nil_score"), "authority_records", ["nil_score"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_authority_records_nil_score"), table_name="authority_records")
    op.drop_column("authority_records", "nil_score")
