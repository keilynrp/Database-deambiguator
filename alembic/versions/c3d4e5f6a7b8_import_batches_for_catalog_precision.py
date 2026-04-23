"""Add import batches for precise catalog portal scoping

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-23
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("domain_id", sa.String(), nullable=False),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("file_format", sa.String(), nullable=True),
        sa.Column("source_label", sa.String(length=200), nullable=True),
        sa.Column("total_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("entity_type_hint", sa.String(), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_import_batches_org_id", "import_batches", ["org_id"])
    op.create_index("ix_import_batches_domain_id", "import_batches", ["domain_id"])
    op.create_index("ix_import_batches_source_type", "import_batches", ["source_type"])
    op.create_index("ix_import_batches_created_at", "import_batches", ["created_at"])

    with op.batch_alter_table("raw_entities") as batch_op:
        batch_op.add_column(sa.Column("import_batch_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_raw_entities_import_batch_id", ["import_batch_id"])
        batch_op.create_foreign_key(
            "fk_raw_entities_import_batch_id",
            "import_batches",
            ["import_batch_id"],
            ["id"],
        )

    with op.batch_alter_table("catalog_portals") as batch_op:
        batch_op.add_column(sa.Column("source_batch_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_catalog_portals_source_batch_id", ["source_batch_id"])
        batch_op.create_foreign_key(
            "fk_catalog_portals_source_batch_id",
            "import_batches",
            ["source_batch_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("catalog_portals") as batch_op:
        batch_op.drop_constraint("fk_catalog_portals_source_batch_id", type_="foreignkey")
        batch_op.drop_index("ix_catalog_portals_source_batch_id")
        batch_op.drop_column("source_batch_id")

    with op.batch_alter_table("raw_entities") as batch_op:
        batch_op.drop_constraint("fk_raw_entities_import_batch_id", type_="foreignkey")
        batch_op.drop_index("ix_raw_entities_import_batch_id")
        batch_op.drop_column("import_batch_id")

    op.drop_index("ix_import_batches_created_at", table_name="import_batches")
    op.drop_index("ix_import_batches_source_type", table_name="import_batches")
    op.drop_index("ix_import_batches_domain_id", table_name="import_batches")
    op.drop_index("ix_import_batches_org_id", table_name="import_batches")
    op.drop_table("import_batches")
