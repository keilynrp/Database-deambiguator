"""drop legacy runtime columns after schema alignment

Revision ID: c7d8e9f0a1b2
Revises: b6c7d8e9f0a1
Create Date: 2026-03-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c7d8e9f0a1b2"
down_revision = "b6c7d8e9f0a1"
branch_labels = None
depends_on = None


def _legacy_row_count(query: str) -> int:
    bind = op.get_bind()
    return int(bind.execute(sa.text(query)).scalar() or 0)


def upgrade() -> None:
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == "sqlite"

    op.execute(
        sa.text(
            """
            UPDATE audit_logs
            SET details = detail
            WHERE details IS NULL AND detail IS NOT NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE branding_settings
            SET accent_color = COALESCE(NULLIF(accent_color, ''), NULLIF(primary_color, ''), '#6366f1')
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE scheduled_reports
            SET recipient_emails = COALESCE(NULLIF(recipient_emails, ''), NULLIF(recipients, ''), '[]')
            WHERE recipients IS NOT NULL
            """
        )
    )

    if _legacy_row_count(
        "SELECT COUNT(*) FROM scheduled_imports WHERE cron_expr IS NOT NULL AND cron_expr <> ''"
    ):
        raise RuntimeError(
            "Cannot drop scheduled_imports.cron_expr while legacy cron-based schedules still exist."
        )

    if _legacy_row_count(
        """
        SELECT COUNT(*)
        FROM scheduled_reports
        WHERE (cron_expr IS NOT NULL AND cron_expr <> '')
           OR template_id IS NOT NULL
        """
    ):
        raise RuntimeError(
            "Cannot drop legacy scheduled_reports columns while cron/template-backed rows still exist."
        )

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_column("detail")

    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.drop_column("primary_color")
        batch_op.drop_column("secondary_color")

    with op.batch_alter_table("scheduled_imports") as batch_op:
        batch_op.drop_column("cron_expr")

    with op.batch_alter_table("scheduled_reports") as batch_op:
        if not is_sqlite:
            batch_op.drop_constraint("scheduled_reports_template_id_fkey", type_="foreignkey")
        batch_op.drop_column("template_id")
        batch_op.drop_column("cron_expr")
        batch_op.drop_column("recipients")


def downgrade() -> None:
    with op.batch_alter_table("scheduled_reports") as batch_op:
        batch_op.add_column(sa.Column("recipients", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("cron_expr", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("template_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "scheduled_reports_template_id_fkey",
            "artifact_templates",
            ["template_id"],
            ["id"],
        )

    with op.batch_alter_table("scheduled_imports") as batch_op:
        batch_op.add_column(sa.Column("cron_expr", sa.String(), nullable=True))

    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.add_column(sa.Column("secondary_color", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("primary_color", sa.String(), nullable=True))

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.add_column(sa.Column("detail", sa.Text(), nullable=True))

    op.execute(
        sa.text(
            """
            UPDATE audit_logs
            SET detail = details
            WHERE detail IS NULL AND details IS NOT NULL
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE branding_settings
            SET primary_color = COALESCE(primary_color, accent_color)
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE scheduled_reports
            SET recipients = COALESCE(recipients, recipient_emails)
            """
        )
    )
