"""add tenant scope columns to operational resources

Revision ID: f0a1b2c3d4e5
Revises: e8f9a0b1c2d3
Create Date: 2026-03-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f0a1b2c3d4e5"
down_revision = "e8f9a0b1c2d3"
branch_labels = None
depends_on = None

_TENANT_TABLES = (
    "store_connections",
    "scheduled_imports",
    "scheduled_reports",
    "web_scraper_configs",
)


def _column_names(bind, table_name: str) -> set[str]:
    return {col["name"] for col in sa.inspect(bind).get_columns(table_name)}


def _index_names(bind, table_name: str) -> set[str]:
    return {idx["name"] for idx in sa.inspect(bind).get_indexes(table_name)}


def _has_org_fk(bind, table_name: str) -> bool:
    for fk in sa.inspect(bind).get_foreign_keys(table_name):
        if fk.get("referred_table") == "organizations" and fk.get("constrained_columns") == ["org_id"]:
            return True
    return False


def _add_org_id_column(table_name: str) -> None:
    bind = op.get_bind()
    idx_name = f"ix_{table_name}_org_id"
    fk_name = f"fk_{table_name}_org_id_organizations"

    columns = _column_names(bind, table_name)
    indexes = _index_names(bind, table_name)
    has_fk = _has_org_fk(bind, table_name)

    with op.batch_alter_table(table_name) as batch_op:
        if "org_id" not in columns:
            batch_op.add_column(sa.Column("org_id", sa.Integer(), nullable=True))
        if not has_fk:
            batch_op.create_foreign_key(
                fk_name,
                "organizations",
                ["org_id"],
                ["id"],
            )
        if idx_name not in indexes:
            batch_op.create_index(idx_name, ["org_id"], unique=False)


def _drop_org_id_column(table_name: str) -> None:
    bind = op.get_bind()
    idx_name = f"ix_{table_name}_org_id"
    fk_name = f"fk_{table_name}_org_id_organizations"

    columns = _column_names(bind, table_name)
    if "org_id" not in columns:
        return

    indexes = _index_names(bind, table_name)
    has_fk = _has_org_fk(bind, table_name)

    with op.batch_alter_table(table_name) as batch_op:
        if idx_name in indexes:
            batch_op.drop_index(idx_name)
        if has_fk:
            batch_op.drop_constraint(fk_name, type_="foreignkey")
        batch_op.drop_column("org_id")


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    for table_name in _TENANT_TABLES:
        _add_org_id_column(table_name)

    if is_sqlite:
        op.execute(
            sa.text(
                """
                UPDATE scheduled_imports
                SET org_id = (
                    SELECT store_connections.org_id
                    FROM store_connections
                    WHERE store_connections.id = scheduled_imports.store_id
                )
                WHERE org_id IS NULL
                """
            )
        )
    else:
        op.execute(
            sa.text(
                """
                UPDATE scheduled_imports AS sched
                SET org_id = stores.org_id
                FROM store_connections AS stores
                WHERE sched.store_id = stores.id
                  AND sched.org_id IS NULL
                """
            )
        )


def downgrade() -> None:
    for table_name in reversed(_TENANT_TABLES):
        _drop_org_id_column(table_name)
