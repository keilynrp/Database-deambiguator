"""sprint_93_embed_widgets

Revision ID: 93b2c3d4e5f6
Revises: 92a1b2c3d4e5
Create Date: 2026-03-15 17:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = '93b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '92a1b2c3d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    existing = bind.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='embed_widgets'"
    )).fetchone()
    if existing is None:
        op.create_table(
            'embed_widgets',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(200), nullable=False),
            sa.Column('widget_type', sa.String(50), nullable=False),
            sa.Column('config', sa.Text, default='{}'),
            sa.Column('public_token', sa.String(36), unique=True, nullable=False),
            sa.Column('allowed_origins', sa.Text, default='*'),
            sa.Column('is_active', sa.Boolean, default=True),
            sa.Column('view_count', sa.Integer, default=0),
            sa.Column('created_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
            sa.Column('created_at', sa.DateTime, nullable=True),
            sa.Column('last_viewed_at', sa.DateTime, nullable=True),
        )


def downgrade() -> None:
    op.drop_table('embed_widgets')
