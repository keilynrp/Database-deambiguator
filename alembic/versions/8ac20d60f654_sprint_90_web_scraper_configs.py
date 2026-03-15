"""sprint_90_web_scraper_configs

Revision ID: 8ac20d60f654
Revises: d1f6eb126a08
Create Date: 2026-03-15 02:23:08.947462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ac20d60f654'
down_revision: Union[str, Sequence[str], None] = 'd1f6eb126a08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add web_scraper_configs table (Sprint 90)."""
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("web_scraper_configs"):
        op.create_table(
            'web_scraper_configs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('url_template', sa.Text(), nullable=False),
            sa.Column('selector_type', sa.String(length=10), nullable=True),
            sa.Column('selector', sa.Text(), nullable=False),
            sa.Column('field_map', sa.Text(), nullable=True),
            sa.Column('rate_limit_secs', sa.Float(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=True),
            sa.Column('last_run_at', sa.DateTime(), nullable=True),
            sa.Column('last_run_status', sa.String(length=20), nullable=True),
            sa.Column('total_runs', sa.Integer(), nullable=True),
            sa.Column('total_enriched', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        with op.batch_alter_table('web_scraper_configs') as batch_op:
            batch_op.create_index('ix_web_scraper_configs_id', ['id'], unique=False)
            batch_op.create_index('ix_web_scraper_configs_is_active', ['is_active'], unique=False)


def downgrade() -> None:
    """Remove web_scraper_configs table."""
    op.drop_table('web_scraper_configs')
