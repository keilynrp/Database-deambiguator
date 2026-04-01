"""
Sprint 90 — Web Scraper Configs router.

Endpoints:
  POST   /scrapers              — create a config (admin+)
  GET    /scrapers              — list all configs (viewer+)
  GET    /scrapers/{id}         — fetch one config (viewer+)
  PUT    /scrapers/{id}         — update config (admin+)
  DELETE /scrapers/{id}         — delete config (admin+)
  POST   /scrapers/{id}/test    — test scraper against a sample label (admin+)
  POST   /scrapers/{id}/run     — trigger bulk run against pending entities (admin+)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.tenant_quotas import assert_org_quota_available
from backend.tenant_access import (
    get_scoped_record,
    persisted_org_id,
    resolve_request_org_id,
    scope_query_to_org,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["scrapers"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ScraperCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    url_template: str = Field(..., min_length=10)
    selector_type: str = Field(default="css", pattern="^(css|xpath)$")
    selector: str = Field(..., min_length=1)
    field_map: dict[str, str] = Field(default_factory=dict)
    rate_limit_secs: float = Field(default=1.0, ge=0.1, le=60.0)
    is_active: bool = True


class ScraperUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    url_template: str | None = None
    selector_type: str | None = Field(None, pattern="^(css|xpath)$")
    selector: str | None = None
    field_map: dict[str, str] | None = None
    rate_limit_secs: float | None = Field(None, ge=0.1, le=60.0)
    is_active: bool | None = None


class ScraperResponse(BaseModel):
    id: int
    name: str
    url_template: str
    selector_type: str
    selector: str
    field_map: dict[str, str]
    rate_limit_secs: float
    is_active: bool
    last_run_at: str | None
    last_run_status: str | None
    total_runs: int
    total_enriched: int
    created_at: str

    model_config = {"from_attributes": True}


class ScraperTestRequest(BaseModel):
    primary_label: str = Field(..., min_length=1, max_length=500)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _serialize(cfg: models.WebScraperConfig) -> dict[str, Any]:
    try:
        field_map = json.loads(cfg.field_map or "{}")
    except (ValueError, TypeError):
        field_map = {}
    return {
        "id": cfg.id,
        "org_id": cfg.org_id,
        "name": cfg.name,
        "url_template": cfg.url_template,
        "selector_type": cfg.selector_type,
        "selector": cfg.selector,
        "field_map": field_map,
        "rate_limit_secs": cfg.rate_limit_secs,
        "is_active": cfg.is_active,
        "last_run_at": cfg.last_run_at.isoformat() if cfg.last_run_at else None,
        "last_run_status": cfg.last_run_status,
        "total_runs": cfg.total_runs or 0,
        "total_enriched": cfg.total_enriched or 0,
        "created_at": cfg.created_at.isoformat() if cfg.created_at else "",
    }


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("/scrapers", status_code=201)
def create_scraper(
    payload: ScraperCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = persisted_org_id(resolve_request_org_id(db, current_user))
    assert_org_quota_available(db, org_id, "scrapers", current_user=current_user)
    cfg = models.WebScraperConfig(
        org_id=org_id,
        name=payload.name,
        url_template=payload.url_template,
        selector_type=payload.selector_type,
        selector=payload.selector,
        field_map=json.dumps(payload.field_map),
        rate_limit_secs=payload.rate_limit_secs,
        is_active=payload.is_active,
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return _serialize(cfg)


@router.get("/scrapers")
def list_scrapers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    active_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    q = scope_query_to_org(db.query(models.WebScraperConfig), models.WebScraperConfig, org_id)
    if active_only:
        q = q.filter(models.WebScraperConfig.is_active == True)  # noqa: E712
    items = q.offset(skip).limit(limit).all()
    return [_serialize(c) for c in items]


@router.get("/scrapers/{scraper_id}")
def get_scraper(
    scraper_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    cfg = get_scoped_record(db, models.WebScraperConfig, scraper_id, org_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Scraper config not found")
    return _serialize(cfg)


@router.put("/scrapers/{scraper_id}")
def update_scraper(
    payload: ScraperUpdate,
    scraper_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = resolve_request_org_id(db, current_user)
    cfg = get_scoped_record(db, models.WebScraperConfig, scraper_id, org_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Scraper config not found")
    data = payload.model_dump(exclude_unset=True)
    if "field_map" in data:
        data["field_map"] = json.dumps(data["field_map"])
    for k, v in data.items():
        setattr(cfg, k, v)
    db.commit()
    db.refresh(cfg)
    return _serialize(cfg)


@router.delete("/scrapers/{scraper_id}")
def delete_scraper(
    scraper_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = resolve_request_org_id(db, current_user)
    cfg = get_scoped_record(db, models.WebScraperConfig, scraper_id, org_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Scraper config not found")
    db.delete(cfg)
    db.commit()
    return {"deleted": scraper_id}


# ── Test endpoint ─────────────────────────────────────────────────────────────

@router.post("/scrapers/{scraper_id}/test")
def test_scraper(
    payload: ScraperTestRequest,
    scraper_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    """
    Run the scraper against a single label and return the scraped fields.
    Does NOT write anything to the database.
    """
    org_id = resolve_request_org_id(db, current_user)
    cfg = get_scoped_record(db, models.WebScraperConfig, scraper_id, org_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Scraper config not found")

    from backend.adapters.web_scraper import ScrapeError, adapter_from_config

    adapter = adapter_from_config(cfg)
    try:
        result = adapter.scrape(payload.primary_label)
        return {"ok": True, "fields": result, "label": payload.primary_label}
    except ScrapeError as exc:
        return {"ok": False, "error": str(exc), "label": payload.primary_label}


# ── Bulk run ──────────────────────────────────────────────────────────────────

@router.post("/scrapers/{scraper_id}/run")
def run_scraper(
    scraper_id: int = Path(..., ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    """
    Synchronously run the scraper against up to *limit* entities whose
    enrichment_status is 'none' or 'failed'. Updates entities in-place.
    """
    org_id = resolve_request_org_id(db, current_user)
    cfg = get_scoped_record(db, models.WebScraperConfig, scraper_id, org_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Scraper config not found")
    if not cfg.is_active:
        raise HTTPException(status_code=400, detail="Scraper is disabled")

    from backend.adapters.web_scraper import ScrapeError, adapter_from_config
    from backend.circuit_breaker import CircuitBreaker, CircuitOpenError

    adapter = adapter_from_config(cfg)
    cb = CircuitBreaker(
        name=f"web_scraper_{cfg.id}",
        failure_threshold=3,
        recovery_timeout=60,
    )

    entities = (
        scope_query_to_org(db.query(models.RawEntity), models.RawEntity, cfg.org_id)
        .filter(models.RawEntity.enrichment_status.in_(["none", "failed"]))
        .limit(limit)
        .all()
    )

    enriched = 0
    errors = 0

    for entity in entities:
        if not entity.primary_label:
            continue
        try:
            fields = cb.call(adapter.scrape, entity.primary_label)
            if fields:
                for field, value in fields.items():
                    if hasattr(entity, field):
                        setattr(entity, field, value)
                entity.enrichment_source = cfg.name
                entity.enrichment_status = "completed"
                enriched += 1
            else:
                entity.enrichment_status = "failed"
                errors += 1
        except CircuitOpenError:
            logger.warning("Circuit open for scraper %s — aborting run", cfg.name)
            break
        except ScrapeError as exc:
            logger.warning("Scrape error for entity %s: %s", entity.id, exc)
            entity.enrichment_status = "failed"
            errors += 1

    cfg.last_run_at = datetime.now(timezone.utc)
    cfg.last_run_status = "ok" if errors == 0 else "error"
    cfg.total_runs = (cfg.total_runs or 0) + 1
    cfg.total_enriched = (cfg.total_enriched or 0) + enriched
    db.commit()

    return {
        "scraper_id": scraper_id,
        "entities_processed": len(entities),
        "enriched": enriched,
        "errors": errors,
    }
