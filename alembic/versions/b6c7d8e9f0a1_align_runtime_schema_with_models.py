"""align runtime schema with current ORM models

Revision ID: b6c7d8e9f0a1
Revises: 94c4d5e6f7a8
Create Date: 2026-03-25
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b6c7d8e9f0a1"
down_revision = "94c4d5e6f7a8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.add_column(sa.Column("entity_type", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("entity_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("details", sa.Text(), nullable=True))

    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.add_column(
            sa.Column("accent_color", sa.String(), nullable=True, server_default="#6366f1")
        )
        batch_op.add_column(
            sa.Column(
                "footer_text",
                sa.String(),
                nullable=True,
                server_default="Universal Knowledge Intelligence Platform",
            )
        )

    with op.batch_alter_table("scheduled_imports") as batch_op:
        batch_op.add_column(
            sa.Column("name", sa.String(), nullable=True, server_default="Scheduled import")
        )
        batch_op.add_column(
            sa.Column("interval_minutes", sa.Integer(), nullable=True, server_default="60")
        )
        batch_op.add_column(
            sa.Column("last_status", sa.String(), nullable=True, server_default="pending")
        )
        batch_op.add_column(sa.Column("last_result", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("total_runs", sa.Integer(), nullable=True, server_default="0")
        )
        batch_op.add_column(
            sa.Column(
                "total_entities_imported",
                sa.Integer(),
                nullable=True,
                server_default="0",
            )
        )

    with op.batch_alter_table("scheduled_reports") as batch_op:
        batch_op.add_column(
            sa.Column("name", sa.String(length=200), nullable=True, server_default="Scheduled report")
        )
        batch_op.add_column(
            sa.Column("domain_id", sa.String(length=64), nullable=True, server_default="default")
        )
        batch_op.add_column(
            sa.Column("format", sa.String(length=10), nullable=True, server_default="pdf")
        )
        batch_op.add_column(
            sa.Column("sections", sa.Text(), nullable=True, server_default="[]")
        )
        batch_op.add_column(sa.Column("report_title", sa.String(length=200), nullable=True))
        batch_op.add_column(
            sa.Column("interval_minutes", sa.Integer(), nullable=True, server_default="1440")
        )
        batch_op.add_column(
            sa.Column("recipient_emails", sa.Text(), nullable=True, server_default="[]")
        )
        batch_op.add_column(sa.Column("next_run_at", sa.DateTime(), nullable=True))
        batch_op.add_column(
            sa.Column("last_status", sa.String(length=20), nullable=True, server_default="pending")
        )
        batch_op.add_column(sa.Column("last_error", sa.Text(), nullable=True))
        batch_op.add_column(
            sa.Column("total_sent", sa.Integer(), nullable=True, server_default="0")
        )

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
            SET accent_color = COALESCE(NULLIF(primary_color, ''), accent_color, '#6366f1'),
                footer_text = COALESCE(NULLIF(footer_text, ''), 'Universal Knowledge Intelligence Platform'),
                platform_name = COALESCE(NULLIF(platform_name, ''), 'UKIP'),
                logo_url = COALESCE(logo_url, ''),
                favicon_url = COALESCE(favicon_url, '')
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE scheduled_imports
            SET name = COALESCE(NULLIF(name, ''), 'Scheduled import #' || id::text),
                interval_minutes = COALESCE(interval_minutes, 60),
                last_status = COALESCE(NULLIF(last_status, ''), 'pending'),
                total_runs = COALESCE(total_runs, 0),
                total_entities_imported = COALESCE(total_entities_imported, 0)
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE scheduled_reports
            SET name = COALESCE(NULLIF(name, ''), 'Scheduled report #' || id::text),
                domain_id = COALESCE(NULLIF(domain_id, ''), 'default'),
                format = COALESCE(NULLIF(format, ''), 'pdf'),
                sections = COALESCE(NULLIF(sections, ''), '[]'),
                report_title = COALESCE(NULLIF(report_title, ''), name),
                interval_minutes = COALESCE(interval_minutes, 1440),
                recipient_emails = COALESCE(NULLIF(recipient_emails, ''), NULLIF(recipients, ''), '[]'),
                last_status = COALESCE(NULLIF(last_status, ''), 'pending'),
                total_sent = COALESCE(total_sent, 0)
            """
        )
    )


def downgrade() -> None:
    with op.batch_alter_table("scheduled_reports") as batch_op:
        batch_op.drop_column("total_sent")
        batch_op.drop_column("last_error")
        batch_op.drop_column("last_status")
        batch_op.drop_column("next_run_at")
        batch_op.drop_column("recipient_emails")
        batch_op.drop_column("interval_minutes")
        batch_op.drop_column("report_title")
        batch_op.drop_column("sections")
        batch_op.drop_column("format")
        batch_op.drop_column("domain_id")
        batch_op.drop_column("name")

    with op.batch_alter_table("scheduled_imports") as batch_op:
        batch_op.drop_column("total_entities_imported")
        batch_op.drop_column("total_runs")
        batch_op.drop_column("last_result")
        batch_op.drop_column("last_status")
        batch_op.drop_column("interval_minutes")
        batch_op.drop_column("name")

    with op.batch_alter_table("branding_settings") as batch_op:
        batch_op.drop_column("footer_text")
        batch_op.drop_column("accent_color")

    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.drop_column("details")
        batch_op.drop_column("entity_id")
        batch_op.drop_column("entity_type")
