"""sprint_87_faceting_no_schema_change

Revision ID: 4e9223aa86cb
Revises: 0001
Create Date: 2026-03-15 01:08:26.389160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e9223aa86cb'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sprint 87: Dynamic faceting — no schema changes (new endpoints only)."""
    pass


def downgrade() -> None:
    pass
