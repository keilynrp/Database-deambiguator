"""
Sprint 92 — Workflow Automation Engine router.

Endpoints:
  POST   /workflows                      — create workflow (admin+)
  GET    /workflows                      — list workflows (viewer+)
  GET    /workflows/{id}                 — fetch one (viewer+)
  PUT    /workflows/{id}                 — update workflow (admin+)
  DELETE /workflows/{id}                 — delete workflow (admin+)
  POST   /workflows/{id}/run             — manually trigger workflow (admin+)
  GET    /workflows/{id}/runs            — execution history (viewer+)
  GET    /workflows/runs/{run_id}        — single run detail (viewer+)
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
from backend.tenant_access import (
    get_scoped_record,
    persisted_org_id,
    resolve_request_org_id,
    scope_query_to_org,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["workflows"])


# ── Schemas ───────────────────────────────────────────────────────────────────

_VALID_TRIGGERS = {"entity.created", "entity.enriched", "entity.flagged", "manual"}
_VALID_CONDITIONS = {"field_equals", "field_contains", "field_empty", "enrichment_status_is"}
_VALID_ACTIONS = {"send_webhook", "tag_entity", "send_alert", "log_only"}


class ConditionSchema(BaseModel):
    type: str = Field(..., pattern="^(field_equals|field_contains|field_empty|enrichment_status_is)$")
    field: str = Field(default="")
    value: str = Field(default="")


class ActionSchema(BaseModel):
    type: str = Field(..., pattern="^(send_webhook|tag_entity|send_alert|log_only)$")
    config: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    is_active: bool = True
    trigger_type: str = Field(..., pattern="^(entity\\.created|entity\\.enriched|entity\\.flagged|manual)$")
    trigger_config: dict[str, Any] = Field(default_factory=dict)
    conditions: list[ConditionSchema] = Field(default_factory=list)
    actions: list[ActionSchema] = Field(default_factory=list)


class WorkflowUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    is_active: bool | None = None
    trigger_type: str | None = Field(None, pattern="^(entity\\.created|entity\\.enriched|entity\\.flagged|manual)$")
    trigger_config: dict[str, Any] | None = None
    conditions: list[ConditionSchema] | None = None
    actions: list[ActionSchema] | None = None


class ManualRunRequest(BaseModel):
    entity_id: int = Field(..., ge=1)


def _serialize(wf: models.Workflow) -> dict:
    return {
        "id": wf.id,
        "name": wf.name,
        "description": wf.description,
        "is_active": wf.is_active,
        "trigger_type": wf.trigger_type,
        "trigger_config": json.loads(wf.trigger_config or "{}"),
        "conditions": json.loads(wf.conditions or "[]"),
        "actions": json.loads(wf.actions or "[]"),
        "org_id": wf.org_id,
        "created_by": wf.created_by,
        "created_at": wf.created_at.isoformat() if wf.created_at else None,
        "last_run_at": wf.last_run_at.isoformat() if wf.last_run_at else None,
        "run_count": wf.run_count,
        "last_run_status": wf.last_run_status,
    }


def _serialize_run(run: models.WorkflowRun) -> dict:
    return {
        "id": run.id,
        "org_id": run.org_id,
        "workflow_id": run.workflow_id,
        "status": run.status,
        "trigger_data": json.loads(run.trigger_data or "{}"),
        "steps_log": json.loads(run.steps_log or "[]"),
        "error": run.error,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


# ── CRUD ──────────────────────────────────────────────────────────────────────

@router.post("/workflows", status_code=201)
def create_workflow(
    payload: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = resolve_request_org_id(db, current_user)
    workflow_org_id = persisted_org_id(org_id)
    wf = models.Workflow(
        org_id=workflow_org_id,
        name=payload.name,
        description=payload.description,
        is_active=payload.is_active,
        trigger_type=payload.trigger_type,
        trigger_config=json.dumps(payload.trigger_config),
        conditions=json.dumps([c.model_dump() for c in payload.conditions]),
        actions=json.dumps([a.model_dump() for a in payload.actions]),
        created_by=current_user.id,
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return _serialize(wf)


@router.get("/workflows")
def list_workflows(
    is_active: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    q = scope_query_to_org(db.query(models.Workflow), models.Workflow, org_id)
    if is_active is not None:
        q = q.filter(models.Workflow.is_active == is_active)
    total = q.count()
    items = q.order_by(models.Workflow.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_serialize(w) for w in items]}


@router.get("/workflows/runs/{run_id}")
def get_run(
    run_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    run = get_scoped_record(db, models.WorkflowRun, run_id, org_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return _serialize_run(run)


@router.get("/workflows/{workflow_id}")
def get_workflow(
    workflow_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    wf = get_scoped_record(db, models.Workflow, workflow_id, org_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _serialize(wf)


@router.put("/workflows/{workflow_id}")
def update_workflow(
    payload: WorkflowUpdate,
    workflow_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = resolve_request_org_id(db, current_user)
    wf = get_scoped_record(db, models.Workflow, workflow_id, org_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if payload.name is not None:
        wf.name = payload.name
    if payload.description is not None:
        wf.description = payload.description
    if payload.is_active is not None:
        wf.is_active = payload.is_active
    if payload.trigger_type is not None:
        wf.trigger_type = payload.trigger_type
    if payload.trigger_config is not None:
        wf.trigger_config = json.dumps(payload.trigger_config)
    if payload.conditions is not None:
        wf.conditions = json.dumps([c.model_dump() for c in payload.conditions])
    if payload.actions is not None:
        wf.actions = json.dumps([a.model_dump() for a in payload.actions])

    db.commit()
    db.refresh(wf)
    return _serialize(wf)


@router.delete("/workflows/{workflow_id}")
def delete_workflow(
    workflow_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    org_id = resolve_request_org_id(db, current_user)
    wf = get_scoped_record(db, models.Workflow, workflow_id, org_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"deleted": True}


# ── Execution ─────────────────────────────────────────────────────────────────

@router.post("/workflows/{workflow_id}/run", status_code=201)
def manual_run(
    payload: ManualRunRequest,
    workflow_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin")),
):
    """Manually trigger a workflow against a specific entity."""
    org_id = resolve_request_org_id(db, current_user)
    wf = get_scoped_record(db, models.Workflow, workflow_id, org_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    entity = get_scoped_record(db, models.RawEntity, payload.entity_id, org_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    from backend.workflow_engine import run_workflow
    run = run_workflow(wf, entity, db, trigger_data={"trigger": "manual", "entity_id": entity.id})
    return _serialize_run(run)


@router.get("/workflows/{workflow_id}/runs")
def list_runs(
    workflow_id: int = Path(..., ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    wf = get_scoped_record(db, models.Workflow, workflow_id, org_id)
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    q = (
        scope_query_to_org(db.query(models.WorkflowRun), models.WorkflowRun, org_id)
        .filter(models.WorkflowRun.workflow_id == workflow_id)
    )
    total = q.count()
    runs = q.order_by(models.WorkflowRun.started_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "items": [_serialize_run(r) for r in runs]}
