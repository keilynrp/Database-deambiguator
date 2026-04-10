"""Add organization benchmark profile settings

Revision ID: f9a0b1c2d3e4
Revises: f6a7b8c9d0e1
Create Date: 2026-04-10 21:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f9a0b1c2d3e4"
down_revision = "f6a7b8c9d0e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("organizations", sa.Column("benchmark_profile_id", sa.String(length=80), nullable=True))
    op.add_column("organizations", sa.Column("benchmark_profile_overrides", sa.Text(), nullable=True))
    op.execute(sa.text("UPDATE organizations SET benchmark_profile_overrides = '{}' WHERE benchmark_profile_overrides IS NULL"))


def downgrade() -> None:
    op.drop_column("organizations", "benchmark_profile_overrides")
    op.drop_column("organizations", "benchmark_profile_id")
