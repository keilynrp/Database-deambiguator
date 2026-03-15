"""baseline — full schema at sprint 86

Revision ID: 0001
Revises:
Create Date: 2026-03-15

This migration stamps the current DB schema (sprints 1-86) as the baseline.
For existing databases, run:  alembic stamp 0001
For fresh databases, run:     alembic upgrade head
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("username", sa.String, unique=True, index=True, nullable=False),
        sa.Column("email", sa.String, unique=True, index=True, nullable=True),
        sa.Column("display_name", sa.String(100), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("role", sa.String, nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("failed_attempts", sa.Integer, nullable=True, server_default="0"),
        sa.Column("locked_until", sa.String, nullable=True),
        sa.Column("org_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── organizations ─────────────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("slug", sa.String, unique=True, nullable=False),
        sa.Column("plan", sa.String, nullable=True, server_default="free"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("settings_json", sa.Text, nullable=True),
    )

    # ── raw_entities ──────────────────────────────────────────────────────────
    op.create_table(
        "raw_entities",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("domain", sa.String, index=True, nullable=True, server_default="default"),
        sa.Column("entity_type", sa.String, index=True, nullable=True),
        sa.Column("primary_label", sa.String, index=True, nullable=True),
        sa.Column("secondary_label", sa.String, nullable=True),
        sa.Column("canonical_id", sa.String, index=True, nullable=True),
        sa.Column("attributes_json", sa.Text, nullable=True, server_default="{}"),
        sa.Column("validation_status", sa.String, index=True, nullable=True, server_default="pending"),
        sa.Column("normalized_json", sa.Text, nullable=True),
        sa.Column("enrichment_doi", sa.String, nullable=True),
        sa.Column("enrichment_citation_count", sa.Integer, nullable=True, server_default="0"),
        sa.Column("enrichment_concepts", sa.Text, nullable=True),
        sa.Column("enrichment_source", sa.String, nullable=True),
        sa.Column("enrichment_status", sa.String, index=True, nullable=True, server_default="none"),
        sa.Column("quality_score", sa.Float, index=True, nullable=True),
        sa.Column("source", sa.String, nullable=True, server_default="user"),
        sa.Column("status", sa.String, index=True, nullable=True),
        sa.Column("brand_capitalized", sa.String, index=True, nullable=True),
        sa.Column("sku", sa.String, index=True, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # ── normalization_rules ───────────────────────────────────────────────────
    op.create_table(
        "normalization_rules",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("field_name", sa.String, nullable=False),
        sa.Column("original_value", sa.String, nullable=False),
        sa.Column("canonical_value", sa.String, nullable=False),
        sa.Column("rule_type", sa.String, nullable=True, server_default="literal"),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── harmonization_logs ────────────────────────────────────────────────────
    op.create_table(
        "harmonization_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("step_name", sa.String, nullable=False),
        sa.Column("step_params", sa.Text, nullable=True),
        sa.Column("affected_count", sa.Integer, nullable=True),
        sa.Column("snapshot_json", sa.Text, nullable=True),
        sa.Column("reverted", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── authority_records ─────────────────────────────────────────────────────
    op.create_table(
        "authority_records",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("field_name", sa.String, nullable=True),
        sa.Column("original_value", sa.String, nullable=True),
        sa.Column("authority_source", sa.String, nullable=True),
        sa.Column("authority_id", sa.String, nullable=True),
        sa.Column("canonical_label", sa.String, nullable=True),
        sa.Column("aliases", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("uri", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=True, server_default="pending"),
        sa.Column("resolution_status", sa.String, nullable=True, server_default="unresolved"),
        sa.Column("score_breakdown", sa.Text, nullable=True),
        sa.Column("evidence", sa.Text, nullable=True),
        sa.Column("merged_sources", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("confirmed_at", sa.DateTime, nullable=True),
    )

    # ── store_connections ─────────────────────────────────────────────────────
    op.create_table(
        "store_connections",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("store_type", sa.String, nullable=False),
        sa.Column("base_url", sa.String, nullable=True),
        sa.Column("consumer_key", sa.String, nullable=True),
        sa.Column("consumer_secret", sa.String, nullable=True),
        sa.Column("api_token", sa.String, nullable=True),
        sa.Column("custom_headers", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("last_sync", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── store_sync_queue ──────────────────────────────────────────────────────
    op.create_table(
        "store_sync_queue",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("store_connections.id"), nullable=False),
        sa.Column("raw_data", sa.Text, nullable=True),
        sa.Column("status", sa.String, nullable=True, server_default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("reviewed_at", sa.DateTime, nullable=True),
    )

    # ── ai_integrations ───────────────────────────────────────────────────────
    op.create_table(
        "ai_integrations",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("provider", sa.String, nullable=False),
        sa.Column("api_key", sa.String, nullable=False),
        sa.Column("model_name", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── enrichment_queue ──────────────────────────────────────────────────────
    op.create_table(
        "enrichment_queue",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("entity_id", sa.Integer, sa.ForeignKey("raw_entities.id"), nullable=False),
        sa.Column("status", sa.String, nullable=True, server_default="pending"),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("processed_at", sa.DateTime, nullable=True),
    )

    # ── audit_logs ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("username", sa.String, nullable=True),
        sa.Column("action", sa.String, nullable=True),
        sa.Column("endpoint", sa.String, nullable=True),
        sa.Column("method", sa.String, nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("ip_address", sa.String, nullable=True),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── annotations ───────────────────────────────────────────────────────────
    op.create_table(
        "annotations",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("entity_id", sa.Integer, sa.ForeignKey("raw_entities.id"), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("is_resolved", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("resolved_by_id", sa.Integer, nullable=True),
        sa.Column("emoji_reactions", sa.Text, nullable=True, server_default="{}"),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── analysis_contexts ─────────────────────────────────────────────────────
    op.create_table(
        "analysis_contexts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("entity_id", sa.Integer, sa.ForeignKey("raw_entities.id"), nullable=False),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("context_text", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("pinned", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── entity_relationships ──────────────────────────────────────────────────
    op.create_table(
        "entity_relationships",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("source_id", sa.Integer, sa.ForeignKey("raw_entities.id"), nullable=False),
        sa.Column("target_id", sa.Integer, sa.ForeignKey("raw_entities.id"), nullable=False),
        sa.Column("relation_type", sa.String, nullable=True),
        sa.Column("weight", sa.Float, nullable=True, server_default="1.0"),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── webhooks ──────────────────────────────────────────────────────────────
    op.create_table(
        "webhooks",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("url", sa.String, nullable=False),
        sa.Column("events", sa.Text, nullable=True),
        sa.Column("secret", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── webhook_logs ──────────────────────────────────────────────────────────
    op.create_table(
        "webhook_logs",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("webhook_id", sa.Integer, sa.ForeignKey("webhooks.id"), nullable=False),
        sa.Column("event", sa.String, nullable=True),
        sa.Column("payload", sa.Text, nullable=True),
        sa.Column("response_status", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── notifications ─────────────────────────────────────────────────────────
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, nullable=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("is_read", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── branding_settings ─────────────────────────────────────────────────────
    op.create_table(
        "branding_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("platform_name", sa.String, nullable=True),
        sa.Column("logo_url", sa.String, nullable=True),
        sa.Column("primary_color", sa.String, nullable=True),
        sa.Column("secondary_color", sa.String, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    # ── artifact_templates ────────────────────────────────────────────────────
    op.create_table(
        "artifact_templates",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("sections", sa.Text, nullable=True),
        sa.Column("default_title", sa.String, nullable=True),
        sa.Column("is_builtin", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── artifacts ─────────────────────────────────────────────────────────────
    op.create_table(
        "artifacts",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("title", sa.String, nullable=False),
        sa.Column("template_id", sa.Integer, sa.ForeignKey("artifact_templates.id"), nullable=True),
        sa.Column("content_json", sa.Text, nullable=True),
        sa.Column("created_by_id", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── dashboards ────────────────────────────────────────────────────────────
    op.create_table(
        "dashboards",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("layout_json", sa.Text, nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=True, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── alert_channels ────────────────────────────────────────────────────────
    op.create_table(
        "alert_channels",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("channel_type", sa.String, nullable=False),
        sa.Column("config_json", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── api_keys ──────────────────────────────────────────────────────────────
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("user_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("key_hash", sa.String, nullable=False, unique=True),
        sa.Column("prefix", sa.String, nullable=False),
        sa.Column("scopes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── scheduled_imports ─────────────────────────────────────────────────────
    op.create_table(
        "scheduled_imports",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("store_id", sa.Integer, sa.ForeignKey("store_connections.id"), nullable=False),
        sa.Column("cron_expr", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime, nullable=True),
        sa.Column("next_run_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── scheduled_reports ─────────────────────────────────────────────────────
    op.create_table(
        "scheduled_reports",
        sa.Column("id", sa.Integer, primary_key=True, index=True),
        sa.Column("template_id", sa.Integer, sa.ForeignKey("artifact_templates.id"), nullable=True),
        sa.Column("cron_expr", sa.String, nullable=False),
        sa.Column("recipients", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=True, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    # ── Full-text search table (dialect-conditional) ──────────────────────────
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite: FTS5 virtual table for high-performance prefix matching
        op.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS search_index
            USING fts5(
                doc_type,
                doc_id   UNINDEXED,
                title,
                body,
                href     UNINDEXED
            )
        """)
    else:
        # PostgreSQL: regular table with GIN index on tsvector for native FTS
        op.execute("""
            CREATE TABLE IF NOT EXISTS search_index (
                doc_type TEXT,
                doc_id   INTEGER,
                title    TEXT,
                body     TEXT,
                href     TEXT
            )
        """)
        op.execute("""
            CREATE INDEX IF NOT EXISTS ix_search_index_vector
            ON search_index
            USING GIN (
                to_tsvector('english',
                    COALESCE(title, '') || ' ' || COALESCE(body, ''))
            )
        """)


def downgrade() -> None:
    # Drop in reverse FK order
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TABLE IF EXISTS search_index CASCADE")
    else:
        op.execute("DROP TABLE IF EXISTS search_index")
    op.drop_table("scheduled_reports")
    op.drop_table("scheduled_imports")
    op.drop_table("api_keys")
    op.drop_table("alert_channels")
    op.drop_table("dashboards")
    op.drop_table("artifacts")
    op.drop_table("artifact_templates")
    op.drop_table("branding_settings")
    op.drop_table("notifications")
    op.drop_table("webhook_logs")
    op.drop_table("webhooks")
    op.drop_table("entity_relationships")
    op.drop_table("analysis_contexts")
    op.drop_table("annotations")
    op.drop_table("audit_logs")
    op.drop_table("enrichment_queue")
    op.drop_table("ai_integrations")
    op.drop_table("store_sync_queue")
    op.drop_table("store_connections")
    op.drop_table("authority_records")
    op.drop_table("harmonization_logs")
    op.drop_table("normalization_rules")
    op.drop_table("raw_entities")
    op.drop_table("organizations")
    op.drop_table("users")
