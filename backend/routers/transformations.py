"""
Transformation engine endpoints.
  POST /transformations/preview   — preview expression on sample rows
  POST /transformations/apply     — apply to all entities in domain
  GET  /transformations/history   — list applied transformations
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.routers.deps import _audit
from backend.transformations.engine import (
    apply_expression, validate_expression,
    TransformError, TRANSFORMABLE_FIELDS,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["harmonization"])

_PREVIEW_SAMPLE = 20

# Sentinel prefix for step_id to identify transformation entries
_TRANSFORM_PREFIX = "transform:"


class TransformPayload(BaseModel):
    field: str = Field(..., min_length=1, max_length=64)
    expression: str = Field(..., min_length=1, max_length=500)
    domain_id: Optional[str] = Field(default=None)


class TransformPreviewResponse(BaseModel):
    original: List[Optional[str]]
    transformed: List[Optional[str]]
    errors: List[Optional[str]]
    sample_size: int
    expression: str
    field: str


@router.post("/transformations/preview", response_model=TransformPreviewResponse)
def preview_transformation(
    payload: TransformPayload,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Apply expression to a sample of 20 values — no DB writes."""
    if payload.field not in TRANSFORMABLE_FIELDS:
        raise HTTPException(
            status_code=422,
            detail=f"Field '{payload.field}' is not transformable. "
                   f"Allowed: {sorted(TRANSFORMABLE_FIELDS)}",
        )
    try:
        validate_expression(payload.expression)
    except TransformError as e:
        raise HTTPException(status_code=422, detail=str(e))

    col = getattr(models.RawEntity, payload.field)
    query = db.query(col).filter(col != None, col != "")
    if payload.domain_id:
        query = query.filter(models.RawEntity.domain == payload.domain_id)

    rows = query.limit(_PREVIEW_SAMPLE).all()
    originals, transformed_vals, errors = [], [], []

    for (val,) in rows:
        originals.append(val)
        try:
            transformed_vals.append(apply_expression(payload.expression, val))
            errors.append(None)
        except TransformError as e:
            transformed_vals.append(None)
            errors.append(str(e))

    return TransformPreviewResponse(
        original=originals,
        transformed=transformed_vals,
        errors=errors,
        sample_size=len(originals),
        expression=payload.expression,
        field=payload.field,
    )


@router.post("/transformations/apply")
def apply_transformation(
    payload: TransformPayload,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Apply expression to ALL matching entities and record in harmonization_logs."""
    if payload.field not in TRANSFORMABLE_FIELDS:
        raise HTTPException(
            status_code=422,
            detail=f"Field '{payload.field}' is not transformable. "
                   f"Allowed: {sorted(TRANSFORMABLE_FIELDS)}",
        )
    try:
        validate_expression(payload.expression)
    except TransformError as e:
        raise HTTPException(status_code=422, detail=str(e))

    col = getattr(models.RawEntity, payload.field)
    query = db.query(models.RawEntity).filter(col != None, col != "")
    if payload.domain_id:
        query = query.filter(models.RawEntity.domain == payload.domain_id)

    entities = query.all()

    # Build params dict for storing in fields_modified
    params = {
        "field": payload.field,
        "expression": payload.expression,
        "domain_id": payload.domain_id,
    }

    # Take snapshot for undo (stored in details)
    snapshot = [
        {"id": e.id, "value": getattr(e, payload.field)}
        for e in entities
    ]

    affected = 0
    errors = 0
    for entity in entities:
        original = getattr(entity, payload.field)
        try:
            new_val = apply_expression(payload.expression, original)
            if new_val != original:
                setattr(entity, payload.field, new_val)
                affected += 1
        except TransformError:
            errors += 1

    # Record in harmonization_logs for history/undo
    # step_id encodes params as JSON for retrieval; fields_modified holds the field name;
    # records_updated holds affected count; details holds the snapshot JSON.
    step_id = _TRANSFORM_PREFIX + str(uuid.uuid4())
    log = models.HarmonizationLog(
        step_id=step_id,
        step_name="transformation",
        records_updated=affected,
        fields_modified=json.dumps(params),
        executed_at=datetime.now(timezone.utc),
        details=json.dumps(snapshot),
        reverted=False,
    )
    db.add(log)

    _audit(
        db, "transformation.apply",
        user_id=current_user.id,
        details={
            "field": payload.field,
            "expression": payload.expression,
            "domain_id": payload.domain_id,
            "affected": affected,
            "errors": errors,
        },
    )
    db.commit()

    return {
        "affected": affected,
        "errors": errors,
        "total_scanned": len(entities),
        "field": payload.field,
        "expression": payload.expression,
        "log_id": log.id,
    }


@router.get("/transformations/history")
def get_transformation_history(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Return history of applied transformations (from harmonization_logs)."""
    rows = (
        db.query(models.HarmonizationLog)
        .filter(models.HarmonizationLog.step_name == "transformation")
        .order_by(models.HarmonizationLog.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "params": json.loads(r.fields_modified or "{}"),
            "affected_count": r.records_updated,
            "reverted": r.reverted,
            "created_at": r.executed_at,
        }
        for r in rows
    ]
