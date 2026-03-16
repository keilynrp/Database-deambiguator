"""add favicon_url to branding_settings

Revision ID: a1b2c3d4e5f6
Revises: 93b2c3d4e5f6
Create Date: 2026-03-16
"""
from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "93b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.add_column(
            sa.Column("favicon_url", sa.String(), nullable=True, server_default="")
        )


def downgrade() -> None:
    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.drop_column("favicon_url")
