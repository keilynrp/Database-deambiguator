"""Tenant scoping baseline for EPIC-012 / US-043."""
from __future__ import annotations

WAVE_ORDER = {1: 0, 2: 1, 3: 2, 4: 3}
TENANT_MODEL_UPDATED_AT = "2026-03-27"

TENANT_SCOPED_RESOURCES = [
    {
        "resource": "raw_entities",
        "model": "RawEntity",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 1,
        "why": "Core tenant-owned dataset; every higher-level workflow depends on it.",
        "touchpoints": ["backend/models.py", "backend/routers/entities.py", "backend/routers/ingest.py"],
    },
    {
        "resource": "entity_relationships",
        "model": "EntityRelationship",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 1,
        "why": "Graph edges must never cross tenants unless both nodes belong to the same organization.",
        "touchpoints": ["backend/models.py", "backend/routers/relationships.py", "backend/graph_analytics.py"],
    },
    {
        "resource": "authority_records",
        "model": "AuthorityRecord",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 1,
        "why": "Authority decisions derive from tenant data and must stay attached to the same tenant context.",
        "touchpoints": ["backend/models.py", "backend/routers/authority.py"],
    },
    {
        "resource": "normalization_rules",
        "model": "NormalizationRule",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 1,
        "why": "Cleanup rules are tenant-specific business logic and cannot leak across organizations.",
        "touchpoints": ["backend/models.py", "backend/routers/harmonization.py", "backend/routers/disambiguation.py"],
    },
    {
        "resource": "harmonization_logs",
        "model": "HarmonizationLog",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 1,
        "why": "Auditability of data changes has to follow the same tenant boundary as the data plane.",
        "touchpoints": ["backend/models.py", "backend/routers/harmonization.py"],
    },
    {
        "resource": "annotations",
        "model": "Annotation",
        "current_scope": "shared by referenced record",
        "target_scope": "org_id required plus author_id",
        "migration_wave": 2,
        "why": "Comments and resolve workflows must inherit tenant ownership from the underlying entity or authority record.",
        "touchpoints": ["backend/models.py", "backend/routers/annotations.py"],
    },
    {
        "resource": "workflows",
        "model": "Workflow",
        "current_scope": "shared by creator role",
        "target_scope": "org_id required plus created_by",
        "migration_wave": 2,
        "why": "Automations operate on tenant data and must be isolated with the rest of the tenant runtime.",
        "touchpoints": ["backend/models.py", "backend/routers/workflows.py", "backend/workflow_engine.py"],
    },
    {
        "resource": "scheduled_reports",
        "model": "ScheduledReport",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 2,
        "why": "Scheduled exports are tenant-facing artifacts and should not mix report definitions across organizations.",
        "touchpoints": ["backend/models.py", "backend/routers/scheduled_reports.py"],
    },
    {
        "resource": "scheduled_imports",
        "model": "ScheduledImport",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 2,
        "why": "Inbound sync jobs are tenant-owned operational state and need isolated queues and status.",
        "touchpoints": ["backend/models.py", "backend/routers/scheduled_imports.py"],
    },
    {
        "resource": "alert_channels",
        "model": "AlertChannel",
        "current_scope": "global",
        "target_scope": "org_id required",
        "migration_wave": 2,
        "why": "Operational and business alerts should route only within the owning tenant context.",
        "touchpoints": ["backend/models.py", "backend/routers/alert_channels.py"],
    },
    {
        "resource": "user_dashboards",
        "model": "UserDashboard",
        "current_scope": "user only",
        "target_scope": "org_id required plus user_id",
        "migration_wave": 3,
        "why": "Dashboard preferences remain personal, but the underlying widgets depend on tenant-scoped data.",
        "touchpoints": ["backend/models.py", "backend/routers/dashboards.py"],
    },
    {
        "resource": "analysis_contexts",
        "model": "AnalysisContext",
        "current_scope": "domain plus user",
        "target_scope": "org_id required plus user_id",
        "migration_wave": 3,
        "why": "Saved contexts combine tenant data with user workflows and must stay within the same organization.",
        "touchpoints": ["backend/models.py", "backend/routers/context.py"],
    },
    {
        "resource": "artifact_templates",
        "model": "ArtifactTemplate",
        "current_scope": "global built-ins plus creator",
        "target_scope": "org_id required for tenant-created templates, null for platform built-ins",
        "migration_wave": 3,
        "why": "Built-ins can stay global, but customer-authored templates belong to a tenant workspace.",
        "touchpoints": ["backend/models.py", "backend/routers/artifacts.py"],
    },
    {
        "resource": "embed_widgets",
        "model": "EmbedWidget",
        "current_scope": "creator only",
        "target_scope": "org_id required plus created_by",
        "migration_wave": 3,
        "why": "Public embeds expose tenant data externally and therefore must carry explicit tenant ownership.",
        "touchpoints": ["backend/models.py", "backend/routers/widgets.py"],
    },
    {
        "resource": "users",
        "model": "User",
        "current_scope": "global account with active org pointer",
        "target_scope": "global account plus explicit active/default org semantics",
        "migration_wave": 4,
        "why": "User remains a control-plane identity, but tenant context must be explicit and consistent for downstream enforcement.",
        "touchpoints": ["backend/models.py", "backend/auth.py", "backend/routers/organizations.py"],
    },
    {
        "resource": "branding_settings_and_notification_settings",
        "model": "BrandingSettings / NotificationSettings",
        "current_scope": "global singleton",
        "target_scope": "control-plane exception until tenant admin surfaces exist",
        "migration_wave": 4,
        "why": "These settings can stay platform-global for now and should only become tenant-scoped once admin UX exists.",
        "touchpoints": ["backend/models.py", "backend/routers/branding.py", "backend/routers/notifications.py"],
    },
]

TENANT_MIGRATION_WAVES = [
    {
        "wave": 1,
        "label": "Core shared data plane",
        "goal": "Attach org_id to the canonical data records that every tenant workflow depends on.",
    },
    {
        "wave": 2,
        "label": "Automation and collaboration state",
        "goal": "Move background jobs, alerts, and collaboration artifacts under the same tenant boundary.",
    },
    {
        "wave": 3,
        "label": "User-owned tenant surfaces",
        "goal": "Keep user preferences while making every derived artifact explicitly tenant-aware.",
    },
    {
        "wave": 4,
        "label": "Control plane and exceptions",
        "goal": "Clarify which resources remain global and how active-org context is enforced consistently.",
    },
]


def _wave_counts(resources: list[dict]) -> dict[str, int]:
    return {
        f"wave_{wave['wave']}": sum(1 for resource in resources if resource["migration_wave"] == wave["wave"])
        for wave in TENANT_MIGRATION_WAVES
    }


def _current_scope_counts(resources: list[dict]) -> dict[str, int]:
    counts = {"global": 0, "user_only": 0, "shared": 0, "control_plane": 0}
    for resource in resources:
        scope = resource["current_scope"]
        if scope == "global":
            counts["global"] += 1
        elif scope == "user only":
            counts["user_only"] += 1
        elif scope.startswith("shared"):
            counts["shared"] += 1
        else:
            counts["control_plane"] += 1
    return counts


def get_tenant_scoping_report() -> dict:
    resources = sorted(
        TENANT_SCOPED_RESOURCES,
        key=lambda resource: (WAVE_ORDER[resource["migration_wave"]], resource["resource"]),
    )
    return {
        "status": "baseline",
        "service": "ukip-backend",
        "updated_at": TENANT_MODEL_UPDATED_AT,
        "target_model": {
            "tenant_anchor": "Organization",
            "active_context": "User.org_id",
            "rules": [
                "Tenant-owned business data should belong to exactly one organization.",
                "Super-admin access remains control-plane only and must bypass tenant filters explicitly.",
                "User-owned preferences may keep user_id, but shared artifacts must also carry org_id.",
            ],
        },
        "migration_waves": TENANT_MIGRATION_WAVES,
        "summary": {
            "total_resources": len(resources),
            "wave_counts": _wave_counts(resources),
            "current_scope_counts": _current_scope_counts(resources),
        },
        "resources": resources,
    }
