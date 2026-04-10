"""Backfill notification state tables for sprint 107

Revision ID: f6a7b8c9d0e1
Revises: e4f5a6b7c8d9
Create Date: 2026-04-09 19:25:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f6a7b8c9d0e1"
down_revision = "e4f5a6b7c8d9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_notification_states" not in tables:
        op.create_table(
            "user_notification_states",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("last_read_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("user_id"),
        )

    if "user_notification_reads" not in tables:
        op.create_table(
            "user_notification_reads",
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("audit_log_id", sa.Integer(), nullable=False),
            sa.Column("read_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("user_id", "audit_log_id"),
        )

    read_indexes = {idx["name"] for idx in inspector.get_indexes("user_notification_reads")} if "user_notification_reads" in set(sa.inspect(bind).get_table_names()) else set()
    if "ix_user_notification_reads_user_id" not in read_indexes:
        op.create_index(
            "ix_user_notification_reads_user_id",
            "user_notification_reads",
            ["user_id"],
            unique=False,
        )
    if "ix_user_notification_reads_audit_log_id" not in read_indexes:
        op.create_index(
            "ix_user_notification_reads_audit_log_id",
            "user_notification_reads",
            ["audit_log_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "user_notification_reads" in tables:
        read_indexes = {idx["name"] for idx in inspector.get_indexes("user_notification_reads")}
        if "ix_user_notification_reads_audit_log_id" in read_indexes:
            op.drop_index("ix_user_notification_reads_audit_log_id", table_name="user_notification_reads")
        if "ix_user_notification_reads_user_id" in read_indexes:
            op.drop_index("ix_user_notification_reads_user_id", table_name="user_notification_reads")
        op.drop_table("user_notification_reads")

    if "user_notification_states" in tables:
        op.drop_table("user_notification_states")
