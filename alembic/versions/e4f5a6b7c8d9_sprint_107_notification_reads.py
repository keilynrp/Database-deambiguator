"""Sprint 107 notification read overrides

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-04-08 21:35:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4f5a6b7c8d9"
down_revision = "d3e4f5a6b7c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_notification_reads",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("audit_log_id", sa.Integer(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("user_id", "audit_log_id"),
    )
    op.create_index(
        "ix_user_notification_reads_user_id",
        "user_notification_reads",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_user_notification_reads_audit_log_id",
        "user_notification_reads",
        ["audit_log_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_notification_reads_audit_log_id", table_name="user_notification_reads")
    op.drop_index("ix_user_notification_reads_user_id", table_name="user_notification_reads")
    op.drop_table("user_notification_reads")
