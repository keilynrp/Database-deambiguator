from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import models


FREE_PLAN = "free"
PRO_PLAN = "pro"
ENTERPRISE_PLAN = "enterprise"

PLAN_LIMITS: dict[str, dict[str, int | None]] = {
    FREE_PLAN: {
        "members": 3,
        "stores": 1,
        "scrapers": 1,
        "scheduled_imports": 1,
        "scheduled_reports": 1,
        "workflows": 3,
        "api_keys_per_user": 2,
        "alert_channels": 1,
    },
    PRO_PLAN: {
        "members": 15,
        "stores": 5,
        "scrapers": 5,
        "scheduled_imports": 10,
        "scheduled_reports": 10,
        "workflows": 15,
        "api_keys_per_user": 10,
        "alert_channels": 5,
    },
    ENTERPRISE_PLAN: {
        "members": None,
        "stores": None,
        "scrapers": None,
        "scheduled_imports": None,
        "scheduled_reports": None,
        "workflows": None,
        "api_keys_per_user": None,
        "alert_channels": None,
    },
}

RESOURCE_DEFINITIONS: list[dict[str, str]] = [
    {
        "resource": "members",
        "label": "Organization members",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "Includes the owner membership. Extra invites are blocked at the plan limit.",
    },
    {
        "resource": "stores",
        "label": "Store connections",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "Counts active and inactive store connections scoped to the organization.",
    },
    {
        "resource": "scrapers",
        "label": "Scraper configs",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "Counts configured web scraper connectors for the organization.",
    },
    {
        "resource": "scheduled_imports",
        "label": "Scheduled imports",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "Automation schedules for store imports are capped per organization.",
    },
    {
        "resource": "scheduled_reports",
        "label": "Scheduled reports",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "Email report schedules are capped per organization.",
    },
    {
        "resource": "workflows",
        "label": "Workflows",
        "scope": "organization",
        "enforcement": "hard",
        "notes": "No-code workflow automations are capped per organization.",
    },
    {
        "resource": "api_keys_per_user",
        "label": "API keys per requesting user",
        "scope": "requesting_user",
        "enforcement": "advisory",
        "notes": "API keys are still user-scoped in the data model, so this is guidance based on the active organization's plan.",
    },
    {
        "resource": "alert_channels",
        "label": "Alert channels",
        "scope": "global_shared",
        "enforcement": "pending_org_scope",
        "notes": "Alert channels are not org-scoped yet. Limit is documented for commercial packaging but not enforced.",
    },
]

ENFORCED_RESOURCES = {
    item["resource"]
    for item in RESOURCE_DEFINITIONS
    if item["enforcement"] == "hard"
}

RESOURCE_LABELS = {item["resource"]: item["label"] for item in RESOURCE_DEFINITIONS}


def normalize_plan(plan: str | None) -> str:
    plan_normalized = (plan or FREE_PLAN).lower()
    return plan_normalized if plan_normalized in PLAN_LIMITS else FREE_PLAN


def get_plan_limits(plan: str | None) -> dict[str, int | None]:
    return dict(PLAN_LIMITS[normalize_plan(plan)])


def _count_resource_usage(
    db: Session,
    resource: str,
    *,
    org_id: int,
    current_user: models.User | None = None,
) -> int | None:
    if resource == "members":
        return (
            db.query(models.OrganizationMember)
            .filter(models.OrganizationMember.org_id == org_id)
            .count()
        )
    if resource == "stores":
        return (
            db.query(models.StoreConnection)
            .filter(models.StoreConnection.org_id == org_id)
            .count()
        )
    if resource == "scrapers":
        return (
            db.query(models.WebScraperConfig)
            .filter(models.WebScraperConfig.org_id == org_id)
            .count()
        )
    if resource == "scheduled_imports":
        return (
            db.query(models.ScheduledImport)
            .filter(models.ScheduledImport.org_id == org_id)
            .count()
        )
    if resource == "scheduled_reports":
        return (
            db.query(models.ScheduledReport)
            .filter(models.ScheduledReport.org_id == org_id)
            .count()
        )
    if resource == "workflows":
        return (
            db.query(models.Workflow)
            .filter(models.Workflow.org_id == org_id)
            .count()
        )
    if resource == "api_keys_per_user":
        if current_user is None:
            return None
        return (
            db.query(models.ApiKey)
            .filter(
                models.ApiKey.user_id == current_user.id,
                models.ApiKey.is_active == True,  # noqa: E712
            )
            .count()
        )
    if resource == "alert_channels":
        return None
    raise ValueError(f"Unsupported quota resource: {resource}")


def _resource_status(*, limit: int | None, usage: int | None, enforcement: str) -> str:
    if enforcement == "pending_org_scope":
        return "pending_model_alignment"
    if enforcement == "advisory":
        if limit is None:
            return "unlimited"
        if usage is None:
            return "advisory"
        return "at_limit" if usage >= limit else "ok"
    if limit is None:
        return "unlimited"
    if usage is None:
        return "unknown"
    return "at_limit" if usage >= limit else "ok"


def build_org_quota_snapshot(
    db: Session,
    org: models.Organization,
    *,
    current_user: models.User | None = None,
) -> dict:
    plan = normalize_plan(org.plan)
    limits = get_plan_limits(plan)
    resources = []

    for definition in RESOURCE_DEFINITIONS:
        resource = definition["resource"]
        limit = limits[resource]
        usage = _count_resource_usage(db, resource, org_id=org.id, current_user=current_user)
        remaining = None if limit is None or usage is None else max(limit - usage, 0)
        resources.append(
            {
                "resource": resource,
                "label": definition["label"],
                "scope": definition["scope"],
                "enforcement": definition["enforcement"],
                "limit": limit,
                "usage": usage,
                "remaining": remaining,
                "status": _resource_status(
                    limit=limit,
                    usage=usage,
                    enforcement=definition["enforcement"],
                ),
                "notes": definition["notes"],
            }
        )

    return {
        "organization": {
            "id": org.id,
            "slug": org.slug,
            "name": org.name,
            "plan": plan,
        },
        "resources": resources,
        "enforced_resources": sorted(ENFORCED_RESOURCES),
        "advisory_resources": sorted(
            item["resource"]
            for item in RESOURCE_DEFINITIONS
            if item["enforcement"] != "hard"
        ),
    }


def assert_org_quota_available(
    db: Session,
    org_id: int | None,
    resource: str,
    *,
    current_user: models.User | None = None,
) -> None:
    if org_id is None:
        return
    if resource not in ENFORCED_RESOURCES:
        return

    org = db.get(models.Organization, org_id)
    if not org or not org.is_active:
        raise HTTPException(status_code=404, detail="Organization not found")

    plan = normalize_plan(org.plan)
    limit = PLAN_LIMITS[plan][resource]
    if limit is None:
        return

    usage = _count_resource_usage(db, resource, org_id=org_id, current_user=current_user) or 0
    if usage >= limit:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Plan limit reached for {RESOURCE_LABELS[resource].lower()} "
                f"on plan '{plan}' ({usage}/{limit})"
            ),
        )
