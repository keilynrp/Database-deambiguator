"""US-071A catalog portals

Revision ID: a7b8c9d0e1f2
Revises: f9a0b1c2d3e4
Create Date: 2026-04-22
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a7b8c9d0e1f2"
down_revision = "f9a0b1c2d3e4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "catalog_portals" not in tables:
        op.create_table(
            "catalog_portals",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
            sa.Column("domain_id", sa.String(length=80), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("slug", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("visibility", sa.String(length=20), nullable=False, server_default="private"),
            sa.Column("query_json", sa.Text(), nullable=True, server_default="{}"),
            sa.Column("featured_facets_json", sa.Text(), nullable=True, server_default="[]"),
            sa.Column("default_sort", sa.String(length=40), nullable=False, server_default="primary_label"),
            sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("slug", name="uq_catalog_portals_slug"),
        )

    indexes = {idx["name"] for idx in inspector.get_indexes("catalog_portals")} if "catalog_portals" in set(sa.inspect(bind).get_table_names()) else set()
    if "ix_catalog_portals_id" not in indexes:
        op.create_index("ix_catalog_portals_id", "catalog_portals", ["id"], unique=False)
    if "ix_catalog_portals_org_id" not in indexes:
        op.create_index("ix_catalog_portals_org_id", "catalog_portals", ["org_id"], unique=False)
    if "ix_catalog_portals_domain_id" not in indexes:
        op.create_index("ix_catalog_portals_domain_id", "catalog_portals", ["domain_id"], unique=False)
    if "ix_catalog_portals_slug" not in indexes:
        op.create_index("ix_catalog_portals_slug", "catalog_portals", ["slug"], unique=True)
    if "ix_catalog_portals_visibility" not in indexes:
        op.create_index("ix_catalog_portals_visibility", "catalog_portals", ["visibility"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "catalog_portals" not in tables:
        return

    indexes = {idx["name"] for idx in inspector.get_indexes("catalog_portals")}
    for index_name in [
        "ix_catalog_portals_visibility",
        "ix_catalog_portals_slug",
        "ix_catalog_portals_domain_id",
        "ix_catalog_portals_org_id",
        "ix_catalog_portals_id",
    ]:
        if index_name in indexes:
            op.drop_index(index_name, table_name="catalog_portals")

    op.drop_table("catalog_portals")
