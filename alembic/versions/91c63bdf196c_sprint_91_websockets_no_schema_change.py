"""sprint_91_websockets_no_schema_change

Revision ID: 91c63bdf196c
Revises: 8ac20d60f654
Create Date: 2026-03-15 14:39:00.452128

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '91c63bdf196c'
down_revision: Union[str, Sequence[str], None] = '8ac20d60f654'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
