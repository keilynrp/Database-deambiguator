"""add tenant scope columns to critical runtime tables

Revision ID: e8f9a0b1c2d3
Revises: c7d8e9f0a1b2
Create Date: 2026-03-28
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e8f9a0b1c2d3"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None

_TENANT_TABLES = (
    "raw_entities",
    "entity_relationships",
    "normalization_rules",
    "harmonization_logs",
    "authority_records",
    "workflows",
    "workflow_runs",
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
                UPDATE entity_relationships
                SET org_id = (
                    SELECT raw_entities.org_id
                    FROM raw_entities
                    WHERE raw_entities.id = entity_relationships.source_id
                )
                WHERE org_id IS NULL
                """
            )
        )
        op.execute(
            sa.text(
                """
                UPDATE workflows
                SET org_id = (
                    SELECT users.org_id
                    FROM users
                    WHERE users.id = workflows.created_by
                )
                WHERE org_id IS NULL AND created_by IS NOT NULL
                """
            )
        )
        op.execute(
            sa.text(
                """
                UPDATE workflow_runs
                SET org_id = (
                    SELECT workflows.org_id
                    FROM workflows
                    WHERE workflows.id = workflow_runs.workflow_id
                )
                WHERE org_id IS NULL
                """
            )
        )
    else:
        op.execute(
            sa.text(
                """
                UPDATE entity_relationships AS rel
                SET org_id = src.org_id
                FROM raw_entities AS src
                WHERE rel.source_id = src.id
                  AND rel.org_id IS NULL
                """
            )
        )
        op.execute(
            sa.text(
                """
                UPDATE workflows AS wf
                SET org_id = users.org_id
                FROM users
                WHERE wf.created_by = users.id
                  AND wf.org_id IS NULL
                """
            )
        )
        op.execute(
            sa.text(
                """
                UPDATE workflow_runs AS runs
                SET org_id = workflows.org_id
                FROM workflows
                WHERE runs.workflow_id = workflows.id
                  AND runs.org_id IS NULL
                """
            )
        )


def downgrade() -> None:
    for table_name in reversed(_TENANT_TABLES):
        _drop_org_id_column(table_name)
