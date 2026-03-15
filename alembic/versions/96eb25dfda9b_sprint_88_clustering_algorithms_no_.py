"""sprint_88_clustering_algorithms_no_schema_change

Revision ID: 96eb25dfda9b
Revises: 4e9223aa86cb
Create Date: 2026-03-15 01:37:41.100025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96eb25dfda9b'
down_revision: Union[str, Sequence[str], None] = '4e9223aa86cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Sprint 88: Additional clustering algorithms (Fingerprint, N-gram, Cologne Phonetic, Metaphone).
    No schema changes required — all new logic lives in backend/clustering/algorithms.py
    and is wired into the existing /disambiguate/{field} endpoint via the 'algorithm' query param.
    """
    pass


def downgrade() -> None:
    """No schema changes to revert."""
    pass
