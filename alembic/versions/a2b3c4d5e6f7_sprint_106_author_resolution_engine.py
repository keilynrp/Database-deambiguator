"""add author resolution engine fields to authority records

Revision ID: a2b3c4d5e6f7
Revises: f0a1b2c3d4e5
Create Date: 2026-03-31
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a2b3c4d5e6f7"
down_revision = "f0a1b2c3d4e5"
branch_labels = None
depends_on = None


def _column_names(bind, table_name: str) -> set[str]:
    return {col["name"] for col in sa.inspect(bind).get_columns(table_name)}


def _index_names(bind, table_name: str) -> set[str]:
    return {idx["name"] for idx in sa.inspect(bind).get_indexes(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _column_names(bind, "authority_records")
    indexes = _index_names(bind, "authority_records")
    authority_records = sa.table(
        "authority_records",
        sa.column("review_required", sa.Boolean()),
    )

    with op.batch_alter_table("authority_records") as batch_op:
        if "resolution_route" not in columns:
            batch_op.add_column(sa.Column("resolution_route", sa.String(), nullable=True))
        if "complexity_score" not in columns:
            batch_op.add_column(sa.Column("complexity_score", sa.Float(), nullable=True))
        if "review_required" not in columns:
            batch_op.add_column(sa.Column("review_required", sa.Boolean(), nullable=True))
        if "nil_reason" not in columns:
            batch_op.add_column(sa.Column("nil_reason", sa.String(), nullable=True))

        if "ix_authority_records_resolution_route" not in indexes:
            batch_op.create_index("ix_authority_records_resolution_route", ["resolution_route"], unique=False)
        if "ix_authority_records_complexity_score" not in indexes:
            batch_op.create_index("ix_authority_records_complexity_score", ["complexity_score"], unique=False)
        if "ix_authority_records_review_required" not in indexes:
            batch_op.create_index("ix_authority_records_review_required", ["review_required"], unique=False)

    op.execute(
        authority_records.update()
        .where(authority_records.c.review_required.is_(None))
        .values(review_required=sa.false())
    )


def downgrade() -> None:
    bind = op.get_bind()
    indexes = _index_names(bind, "authority_records")
    columns = _column_names(bind, "authority_records")

    with op.batch_alter_table("authority_records") as batch_op:
        if "ix_authority_records_review_required" in indexes:
            batch_op.drop_index("ix_authority_records_review_required")
        if "ix_authority_records_complexity_score" in indexes:
            batch_op.drop_index("ix_authority_records_complexity_score")
        if "ix_authority_records_resolution_route" in indexes:
            batch_op.drop_index("ix_authority_records_resolution_route")
        if "nil_reason" in columns:
            batch_op.drop_column("nil_reason")
        if "review_required" in columns:
            batch_op.drop_column("review_required")
        if "complexity_score" in columns:
            batch_op.drop_column("complexity_score")
        if "resolution_route" in columns:
            batch_op.drop_column("resolution_route")
