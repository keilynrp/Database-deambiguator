"""
Sprint 95/104 onboarding API.

Auto-detects user progress from existing DB state with no extra schema.

GET /onboarding/status returns:
  - step list with completion flags and percentage
  - focused commercial MVP metadata
  - recommended fast-path journey
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


_STEPS = [
    {
        "key": "import_data",
        "label": "Import publication data",
        "description": "Upload CSV, Excel, BibTeX, or RIS to load publications, authors, and affiliations.",
        "href": "/import-export",
        "icon": "upload",
    },
    {
        "key": "enrich_entity",
        "label": "Enrich a research record",
        "description": "Run enrichment to pull publication, author, and affiliation metadata from academic sources.",
        "href": "/",
        "icon": "sparkles",
    },
    {
        "key": "create_rule",
        "label": "Create a harmonization rule",
        "description": "Normalize author, affiliation, or source labels so future imports stay cleaner.",
        "href": "/disambiguation",
        "icon": "adjustments",
    },
    {
        "key": "create_workflow",
        "label": "Create a recurring workflow",
        "description": "Automate a recurring import, alert, or cleanup step for your research portfolio.",
        "href": "/workflows",
        "icon": "bolt",
    },
    {
        "key": "explore_analytics",
        "label": "Review portfolio analytics",
        "description": "Open dashboard KPIs to validate coverage, trends, and institutional gaps.",
        "href": "/analytics/dashboard",
        "icon": "chart",
    },
]

_COMMERCIAL_MVP = {
    "key": "research_intelligence",
    "label": "Research Intelligence",
    "summary": (
        "Initial commercial focus for universities, research offices, libraries, "
        "and innovation teams that need a clean publication portfolio before "
        "they can trust analytics or recurring reporting."
    ),
    "ideal_customer": "Research office, library analytics, or innovation strategy team",
    "initial_dataset": "CSV, Excel, BibTeX, or RIS with publications, authors, and affiliations",
    "time_to_first_value": "30-60 minutes",
    "primary_outcomes": [
        "Consolidate publication records into one working dataset",
        "Enrich authors, affiliations, and bibliographic metadata",
        "Surface portfolio KPIs, coverage gaps, and recurring operations",
    ],
}

_JOURNEY = [
    {
        "key": "load_portfolio",
        "label": "Load a publication portfolio",
        "description": "Bring the latest export from your research reporting workflow or bibliography manager.",
        "href": "/import-export",
    },
    {
        "key": "enrich_and_resolve",
        "label": "Enrich authors and affiliations",
        "description": "Run enrichment and authority review so the first dashboard is based on stronger metadata.",
        "href": "/authority",
    },
    {
        "key": "normalize_recurring_noise",
        "label": "Capture one reusable normalization rule",
        "description": "Turn the first repeated cleanup into a rule so the next import takes less manual effort.",
        "href": "/disambiguation",
    },
    {
        "key": "review_portfolio_health",
        "label": "Review portfolio KPIs and automate follow-up",
        "description": "Validate coverage in analytics and set a workflow or report for the next reporting cycle.",
        "href": "/analytics/dashboard",
    },
]


def _check_steps(db: Session, user: models.User) -> list[dict]:
    """Auto-detect which steps are complete from existing DB state."""
    entity_count = db.query(func.count(models.RawEntity.id)).scalar() or 0
    enriched_count = (
        db.query(func.count(models.RawEntity.id))
        .filter(models.RawEntity.enrichment_status == "completed")
        .scalar() or 0
    )
    rule_count = db.query(func.count(models.NormalizationRule.id)).scalar() or 0
    workflow_count = db.query(func.count(models.Workflow.id)).scalar() or 0
    analytics_visited = (
        db.query(models.AuditLog)
        .filter(
            models.AuditLog.endpoint.like("%/dashboard/summary%"),
            models.AuditLog.user_id == user.id,
        )
        .first()
    ) is not None

    completion = {
        "import_data": entity_count > 0,
        "enrich_entity": enriched_count > 0,
        "create_rule": rule_count > 0,
        "create_workflow": workflow_count > 0,
        "explore_analytics": analytics_visited,
    }

    return [{**step, "completed": completion.get(step["key"], False)} for step in _STEPS]


def _next_recommended_step(steps: list[dict]) -> dict | None:
    """Return the fastest next move for the focused commercial MVP."""
    for step in steps:
        if not step["completed"]:
            return {
                "key": step["key"],
                "label": step["label"],
                "description": step["description"],
                "href": step["href"],
                "reason": (
                    "This is the next fastest move to reach first value for the "
                    "research intelligence MVP."
                ),
            }
    return None


@router.get("/status")
def onboarding_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Return onboarding checklist with auto-detected completion status.
    No DB writes, purely derived from existing tables.
    """
    steps = _check_steps(db, current_user)
    completed = sum(1 for step in steps if step["completed"])
    return {
        "steps": steps,
        "completed": completed,
        "total": len(steps),
        "percent": round(completed / len(steps) * 100) if steps else 0,
        "all_done": completed == len(steps),
        "commercial_mvp": _COMMERCIAL_MVP,
        "journey": _JOURNEY,
        "next_recommended_step": _next_recommended_step(steps),
    }
