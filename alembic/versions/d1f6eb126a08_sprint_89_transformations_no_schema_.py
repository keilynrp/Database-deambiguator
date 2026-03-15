"""sprint_89_transformations_no_schema_change

Revision ID: d1f6eb126a08
Revises: 96eb25dfda9b
Create Date: 2026-03-15 02:08:44.169121

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1f6eb126a08'
down_revision: Union[str, Sequence[str], None] = '96eb25dfda9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sprint 89: Transformation engine — no schema changes (reuses harmonization_logs)."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
