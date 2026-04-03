"""
Authority resolution layer endpoints.
  POST /authority/resolve
  POST /authority/resolve/batch
  GET  /authority/queue/summary
  POST /authority/records/bulk-confirm
  POST /authority/records/bulk-reject
  GET  /authority/records
  POST /authority/records/{record_id}/confirm
  POST /authority/records/{record_id}/reject
  DELETE /authority/records/{record_id}
  GET  /authority/metrics
  GET  /authority/{field}
"""
import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from sqlalchemy import func, inspect, text
from sqlalchemy.orm import Session

from backend import database, models, schemas
from backend.auth import get_current_user, require_role
from backend.authority.author_resolution import summarize_author_resolution
from backend.authority.base import ResolveContext as _AuthorityContext
from backend.authority.hierarchical_fallback import apply_hierarchical_fallback
from backend.authority.resolver import resolve_all as _authority_resolve_all
from backend.database import get_db
from backend.routers.deps import _audit, _build_disambig_groups, _serialize_authority_record
from backend.routers.limiter import limiter
from backend.tenant_access import (
    add_org_sql_filter,
    get_scoped_record,
    persisted_org_id,
    resolve_request_org_id,
    scope_query_to_org,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["authority"])

_FIELD_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


# ── Authority resolution ──────────────────────────────────────────────────────

@router.post("/authority/resolve", status_code=201, tags=["authority"])
@limiter.limit("60/minute")
def resolve_authority(
    request: Request,
    payload: schemas.AuthorityResolveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """
    Query all authority sources in parallel for a given value and persist
    the candidates with status='pending'. Returns the persisted records.
    """
    org_id = resolve_request_org_id(db, current_user)
    record_org_id = persisted_org_id(org_id)
    ctx = _AuthorityContext(
        affiliation=payload.context_affiliation,
        orcid_hint=payload.context_orcid_hint,
        doi=payload.context_doi,
        year=payload.context_year,
    )
    candidates = _authority_resolve_all(payload.value, payload.entity_type.value, ctx)
    candidates = apply_hierarchical_fallback(payload.value, payload.entity_type.value, candidates)

    records = []
    for c in candidates:
        rec = models.AuthorityRecord(
            org_id=record_org_id,
            field_name=payload.field_name,
            original_value=payload.value,
            authority_source=c.authority_source,
            authority_id=c.authority_id,
            canonical_label=c.canonical_label,
            aliases=json.dumps(c.aliases),
            description=c.description,
            confidence=c.confidence,
            uri=c.uri,
            status="pending",
            resolution_status=c.resolution_status,
            score_breakdown=json.dumps(c.score_breakdown),
            evidence=json.dumps(c.evidence),
            merged_sources=json.dumps(c.merged_sources),
            hierarchy_distance=c.hierarchy_distance,
        )
        db.add(rec)
        records.append(rec)

    db.commit()
    for rec in records:
        db.refresh(rec)

    return [_serialize_authority_record(r) for r in records]


@router.post("/authority/authors/resolve", status_code=201, tags=["authority"])
@limiter.limit("60/minute")
def resolve_author_profile(
    request: Request,
    payload: schemas.AuthorResolveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """
    Author-only adaptive resolution baseline.

    Reuses the existing authority resolver/scoring pipeline, then adds a
    deterministic routing heuristic that classifies the case as fast/hybrid/LLM
    or manual review. The response keeps all persisted records for auditability.
    """
    org_id = resolve_request_org_id(db, current_user)
    record_org_id = persisted_org_id(org_id)
    ctx = _AuthorityContext(
        affiliation=payload.context_affiliation,
        orcid_hint=payload.context_orcid_hint,
        doi=payload.context_doi,
        year=payload.context_year,
    )
    candidates = _authority_resolve_all(payload.value, "person", ctx)
    summary = summarize_author_resolution(candidates, ctx)

    records: list[models.AuthorityRecord] = []
    if candidates:
        for c in candidates:
            rec = models.AuthorityRecord(
                org_id=record_org_id,
                field_name=payload.field_name,
                original_value=payload.value,
                authority_source=c.authority_source,
                authority_id=c.authority_id,
                canonical_label=c.canonical_label,
                aliases=json.dumps(c.aliases),
                description=c.description,
                confidence=c.confidence,
                uri=c.uri,
                status="pending",
                resolution_status=c.resolution_status,
                score_breakdown=json.dumps(c.score_breakdown),
                evidence=json.dumps(c.evidence),
                merged_sources=json.dumps(c.merged_sources),
                resolution_route=summary.resolution_route,
                complexity_score=summary.complexity_score,
                review_required=summary.review_required,
                nil_reason=summary.nil_reason,
                nil_score=summary.nil_score,
            )
            db.add(rec)
            records.append(rec)
    else:
        nil_record = models.AuthorityRecord(
            org_id=record_org_id,
            field_name=payload.field_name,
            original_value=payload.value,
            authority_source="internal_nil",
            authority_id="NIL",
            canonical_label=payload.value,
            aliases="[]",
            description="No external authority candidates were returned for this author query.",
            confidence=0.0,
            uri=None,
            status="pending",
            resolution_status="unresolved",
            score_breakdown="{}",
            evidence=json.dumps([f"nil_reason:{summary.nil_reason or 'no_candidates'}"]),
            merged_sources="[]",
            resolution_route=summary.resolution_route,
            complexity_score=summary.complexity_score,
            review_required=summary.review_required,
            nil_reason=summary.nil_reason or "no_candidates",
            nil_score=summary.nil_score,
        )
        db.add(nil_record)
        records.append(nil_record)

    db.commit()
    for rec in records:
        db.refresh(rec)

    serialized = [_serialize_authority_record(r) for r in records]
    winning = serialized[0] if serialized else None
    runner_up = serialized[1] if len(serialized) > 1 else None

    return {
        "query": {
            "field_name": payload.field_name,
            "value": payload.value,
            "entity_type": "person",
        },
        "resolution_route": summary.resolution_route,
        "complexity_score": summary.complexity_score,
        "review_required": summary.review_required,
        "nil_reason": summary.nil_reason,
        "nil_score": summary.nil_score,
        "records_created": len(serialized),
        "winning_record": winning,
        "runner_up_record": runner_up,
        "records": serialized,
    }


@router.post("/authority/resolve/batch", status_code=201, tags=["authority"])
def resolve_authority_batch(
    payload: schemas.BatchResolveRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """
    Resolve all distinct values of a field against external authority sources.
    """
    org_id = resolve_request_org_id(db, current_user)
    record_org_id = persisted_org_id(org_id)
    field = payload.field_name
    entity_type = payload.entity_type.value

    if not _FIELD_RE.match(field):
        raise HTTPException(status_code=422, detail=f"Invalid field name: {field!r}")

    _entity_cols = {col["name"] for col in inspect(db.get_bind()).get_columns("raw_entities")}
    if field not in _entity_cols:
        raise HTTPException(status_code=422, detail=f"Field '{field}' not found in entity table")

    query_text = (
        f'SELECT DISTINCT "{field}" FROM raw_entities '
        f'WHERE "{field}" IS NOT NULL AND "{field}" != \'\''
    )
    params: dict[str, object] = {}
    where_clauses: list[str] = []
    add_org_sql_filter(where_clauses, params, org_id)
    if where_clauses:
        query_text += " AND " + " AND ".join(where_clauses)
    rows = db.execute(text(query_text), params).fetchall()
    all_values = [row[0] for row in rows if row[0]]

    already_existed = 0
    if payload.skip_existing and all_values:
        existing_values = {
            r.original_value
            for r in scope_query_to_org(
                db.query(models.AuthorityRecord.original_value), models.AuthorityRecord, org_id
            ).filter(
                models.AuthorityRecord.field_name == field,
                models.AuthorityRecord.status.in_(["pending", "confirmed"]),
            ).all()
        }
        filtered = [v for v in all_values if v not in existing_values]
        already_existed = len(all_values) - len(filtered)
        all_values = filtered

    to_resolve = all_values[: payload.limit]
    skipped = len(all_values) - len(to_resolve)

    ctx = _AuthorityContext()
    new_records: list[models.AuthorityRecord] = []

    for value in to_resolve:
        candidates = _authority_resolve_all(value, entity_type, ctx)
        candidates = apply_hierarchical_fallback(value, entity_type, candidates)
        for c in candidates:
            rec = models.AuthorityRecord(
                org_id=record_org_id,
                field_name=field,
                original_value=value,
                authority_source=c.authority_source,
                authority_id=c.authority_id,
                canonical_label=c.canonical_label,
                aliases=json.dumps(c.aliases),
                description=c.description,
                confidence=c.confidence,
                uri=c.uri,
                status="pending",
                resolution_status=c.resolution_status,
                score_breakdown=json.dumps(c.score_breakdown),
                evidence=json.dumps(c.evidence),
                merged_sources=json.dumps(c.merged_sources),
                hierarchy_distance=c.hierarchy_distance,
            )
            db.add(rec)
            new_records.append(rec)

    db.commit()
    for rec in new_records:
        db.refresh(rec)

    return {
        "field_name":          field,
        "entity_type":         entity_type,
        "resolved_count":      len(to_resolve),
        "skipped_count":       skipped,
        "already_existed_count": already_existed,
        "records_created":     len(new_records),
        "records":             [_serialize_authority_record(r) for r in new_records],
    }


@router.get("/authority/queue/summary", tags=["authority"])
def authority_queue_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Aggregated queue stats by field."""
    org_id = resolve_request_org_id(db, current_user)
    rows = scope_query_to_org(
        db.query(
            models.AuthorityRecord.field_name,
            models.AuthorityRecord.status,
            func.count(models.AuthorityRecord.id),
            func.avg(models.AuthorityRecord.confidence),
        ),
        models.AuthorityRecord,
        org_id,
    ).group_by(
        models.AuthorityRecord.field_name,
        models.AuthorityRecord.status,
    ).all()

    field_map: dict[str, dict] = {}
    totals = {"pending": 0, "confirmed": 0, "rejected": 0}

    for field_name, status, count, avg_conf in rows:
        if field_name not in field_map:
            field_map[field_name] = {
                "field_name": field_name,
                "pending": 0, "confirmed": 0, "rejected": 0,
                "avg_confidence": 0.0,
            }
        if status in field_map[field_name]:
            field_map[field_name][status] = count
        if status in totals:
            totals[status] += count

    avg_rows = scope_query_to_org(
        db.query(
            models.AuthorityRecord.field_name,
            func.avg(models.AuthorityRecord.confidence),
        ),
        models.AuthorityRecord,
        org_id,
    ).group_by(models.AuthorityRecord.field_name).all()
    for field_name, avg_conf in avg_rows:
        if field_name in field_map:
            field_map[field_name]["avg_confidence"] = round(float(avg_conf or 0.0), 3)

    by_field = sorted(field_map.values(), key=lambda x: x["pending"], reverse=True)

    return {
        "total_pending":   totals["pending"],
        "total_confirmed": totals["confirmed"],
        "total_rejected":  totals["rejected"],
        "by_field":        by_field,
    }


@router.get("/authority/authors/review-queue", tags=["authority"])
def author_review_queue(
    status: Optional[str] = Query("pending", pattern="^(pending|confirmed|rejected)$"),
    review_required: Optional[bool] = Query(True),
    route: Optional[str] = Query(None, pattern="^(fast_path|hybrid_path|llm_path|manual_review)$"),
    nil_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Author-only operational queue.

    This is intentionally scoped to records created by the adaptive author
    pipeline (identified by a non-null `resolution_route`). It gives the
    frontend a stable review surface without disturbing the legacy authority
    endpoints used for generic entity reconciliation.
    """
    org_id = resolve_request_org_id(db, current_user)
    base_q = scope_query_to_org(db.query(models.AuthorityRecord), models.AuthorityRecord, org_id).filter(
        models.AuthorityRecord.resolution_route.is_not(None)
    )

    summary_by_route = {
        row[0]: row[1]
        for row in base_q.with_entities(
            models.AuthorityRecord.resolution_route,
            func.count(models.AuthorityRecord.id),
        ).group_by(
            models.AuthorityRecord.resolution_route
        ).all()
        if row[0]
    }
    summary_by_status = {
        row[0]: row[1]
        for row in base_q.with_entities(
            models.AuthorityRecord.status,
            func.count(models.AuthorityRecord.id),
        ).group_by(
            models.AuthorityRecord.status
        ).all()
        if row[0]
    }
    summary = {
        "total_records": base_q.count(),
        "pending_review": base_q.filter(
            models.AuthorityRecord.status == "pending",
            models.AuthorityRecord.review_required == True,  # noqa: E712
        ).count(),
        "nil_cases": base_q.filter(models.AuthorityRecord.nil_reason.is_not(None)).count(),
        "by_nil_reason": {
            row[0]: row[1]
            for row in base_q.with_entities(
                models.AuthorityRecord.nil_reason,
                func.count(models.AuthorityRecord.id),
            ).filter(
                models.AuthorityRecord.nil_reason.is_not(None)
            ).group_by(
                models.AuthorityRecord.nil_reason
            ).all()
            if row[0]
        },
        "by_route": summary_by_route,
        "by_status": summary_by_status,
    }

    q = base_q
    if status:
        q = q.filter(models.AuthorityRecord.status == status)
    if review_required is not None:
        q = q.filter(models.AuthorityRecord.review_required == review_required)
    if route:
        q = q.filter(models.AuthorityRecord.resolution_route == route)
    if nil_only:
        q = q.filter(models.AuthorityRecord.nil_reason.is_not(None))

    total = q.count()
    records = q.order_by(
        models.AuthorityRecord.review_required.desc(),
        models.AuthorityRecord.complexity_score.desc(),
        models.AuthorityRecord.confidence.desc(),
        models.AuthorityRecord.id.desc(),
    ).offset(skip).limit(limit).all()

    return {
        "total": total,
        "records": [_serialize_authority_record(r) for r in records],
        "summary": summary,
    }


@router.get("/authority/authors/metrics", tags=["authority"])
def author_resolution_metrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Operational metrics for the adaptive author resolution engine only.

    This intentionally excludes legacy/generic authority rows by requiring
    `resolution_route` to be present.
    """
    org_id = resolve_request_org_id(db, current_user)
    base_q = scope_query_to_org(db.query(models.AuthorityRecord), models.AuthorityRecord, org_id).filter(
        models.AuthorityRecord.resolution_route.is_not(None)
    )

    total = base_q.count()
    pending_review = base_q.filter(
        models.AuthorityRecord.status == "pending",
        models.AuthorityRecord.review_required == True,  # noqa: E712
    ).count()
    nil_cases = base_q.filter(models.AuthorityRecord.nil_reason.is_not(None)).count()

    by_route = {
        row[0]: row[1]
        for row in base_q.with_entities(
            models.AuthorityRecord.resolution_route,
            func.count(models.AuthorityRecord.id),
        ).group_by(
            models.AuthorityRecord.resolution_route
        ).all()
        if row[0]
    }
    by_status = {
        row[0]: row[1]
        for row in base_q.with_entities(
            models.AuthorityRecord.status,
            func.count(models.AuthorityRecord.id),
        ).group_by(
            models.AuthorityRecord.status
        ).all()
        if row[0]
    }
    by_nil_reason = {
        row[0]: row[1]
        for row in base_q.with_entities(
            models.AuthorityRecord.nil_reason,
            func.count(models.AuthorityRecord.id),
        ).filter(
            models.AuthorityRecord.nil_reason.is_not(None)
        ).group_by(
            models.AuthorityRecord.nil_reason
        ).all()
        if row[0]
    }

    avg_confidence = base_q.with_entities(func.avg(models.AuthorityRecord.confidence)).scalar() or 0.0
    avg_complexity = base_q.with_entities(func.avg(models.AuthorityRecord.complexity_score)).scalar() or 0.0
    avg_nil_score = base_q.with_entities(func.avg(models.AuthorityRecord.nil_score)).scalar() or 0.0
    confirmed = by_status.get("confirmed", 0)
    rejected = by_status.get("rejected", 0)

    return {
        "total_records": total,
        "pending_review": pending_review,
        "nil_cases": nil_cases,
        "avg_confidence": round(float(avg_confidence), 3),
        "avg_complexity": round(float(avg_complexity), 3),
        "avg_nil_score": round(float(avg_nil_score), 3),
        "review_rate": round(pending_review / total, 3) if total > 0 else 0.0,
        "nil_rate": round(nil_cases / total, 3) if total > 0 else 0.0,
        "confirm_rate": round(confirmed / total, 3) if total > 0 else 0.0,
        "reject_rate": round(rejected / total, 3) if total > 0 else 0.0,
        "by_nil_reason": by_nil_reason,
        "by_route": by_route,
        "by_status": by_status,
    }


@router.get("/authority/authors/review-queue/{record_id}/compare", tags=["authority"])
def author_review_compare(
    record_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Compare an author-engine record against sibling candidates from the same
    original query value. This supports lightweight reviewer workflows without
    introducing a heavier dedicated compare model.
    """
    org_id = resolve_request_org_id(db, current_user)
    subject = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
    if subject is None or subject.resolution_route is None:
        raise HTTPException(status_code=404, detail="Author review record not found")

    siblings = scope_query_to_org(
        db.query(models.AuthorityRecord),
        models.AuthorityRecord,
        org_id,
    ).filter(
        models.AuthorityRecord.resolution_route.is_not(None),
        models.AuthorityRecord.field_name == subject.field_name,
        models.AuthorityRecord.original_value == subject.original_value,
        models.AuthorityRecord.id != subject.id,
    ).order_by(
        models.AuthorityRecord.confidence.desc(),
        models.AuthorityRecord.id.desc(),
    ).limit(5).all()

    return {
        "subject": _serialize_authority_record(subject),
        "peers": [_serialize_authority_record(r) for r in siblings],
        "peer_count": len(siblings),
    }


@router.post("/authority/records/bulk-confirm", tags=["authority"])
def bulk_confirm_authority_records(
    payload: schemas.BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Confirm multiple authority records in one request."""
    org_id = resolve_request_org_id(db, current_user)
    confirmed = 0
    rules_created = 0
    now = datetime.now(timezone.utc).isoformat()

    for record_id in payload.ids:
        rec = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
        if rec is None or rec.status == "confirmed":
            continue
        rec.status = "confirmed"
        rec.confirmed_at = now
        confirmed += 1

        if payload.also_create_rules:
            existing = scope_query_to_org(
                db.query(models.NormalizationRule), models.NormalizationRule, org_id
            ).filter(
                models.NormalizationRule.field_name == rec.field_name,
                models.NormalizationRule.original_value == rec.original_value,
            ).first()
            if not existing:
                db.add(models.NormalizationRule(
                    org_id=rec.org_id,
                    field_name=rec.field_name,
                    original_value=rec.original_value,
                    normalized_value=rec.canonical_label,
                    is_regex=False,
                ))
                rules_created += 1

    db.commit()
    return {"confirmed": confirmed, "rules_created": rules_created}


@router.post("/authority/records/bulk-reject", tags=["authority"])
def bulk_reject_authority_records(
    payload: schemas.BulkActionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Reject multiple authority records in one request."""
    org_id = resolve_request_org_id(db, current_user)
    rejected = 0
    for record_id in payload.ids:
        rec = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
        if rec is None or rec.status == "rejected":
            continue
        rec.status = "rejected"
        rejected += 1

    db.commit()
    return {"rejected": rejected}


@router.get("/authority/records", tags=["authority"])
def list_authority_records(
    field_name: Optional[str] = Query(None, max_length=64),
    status: Optional[str] = Query(None, pattern="^(pending|confirmed|rejected)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List persisted authority candidates with optional filtering."""
    org_id = resolve_request_org_id(db, current_user)
    q = scope_query_to_org(db.query(models.AuthorityRecord), models.AuthorityRecord, org_id)
    if field_name:
        q = q.filter(models.AuthorityRecord.field_name == field_name)
    if status:
        q = q.filter(models.AuthorityRecord.status == status)
    q = q.order_by(models.AuthorityRecord.confidence.desc())
    total = q.count()
    records = q.offset(skip).limit(limit).all()
    return {
        "total":   total,
        "records": [_serialize_authority_record(r) for r in records],
    }


@router.post("/authority/records/{record_id}/confirm", tags=["authority"])
def confirm_authority_record(
    record_id: int = Path(ge=1),
    payload: schemas.AuthorityConfirmRequest = schemas.AuthorityConfirmRequest(),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Confirm a candidate as the authoritative form."""
    org_id = resolve_request_org_id(db, current_user)
    rec = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="AuthorityRecord not found")

    rec.status = "confirmed"
    rec.confirmed_at = datetime.now(timezone.utc).isoformat()

    rule_created = False
    if payload.also_create_rule:
        existing = scope_query_to_org(
            db.query(models.NormalizationRule), models.NormalizationRule, org_id
        ).filter(
            models.NormalizationRule.field_name == rec.field_name,
            models.NormalizationRule.original_value == rec.original_value,
        ).first()
        if not existing:
            db.add(models.NormalizationRule(
                org_id=rec.org_id,
                field_name=rec.field_name,
                original_value=rec.original_value,
                normalized_value=rec.canonical_label,
                is_regex=False,
            ))
            rule_created = True

    _audit(
        db, "authority.confirm",
        user_id=current_user.id,
        entity_type="authority_record",
        entity_id=record_id,
        details={"canonical_label": rec.canonical_label, "rule_created": rule_created},
    )
    db.commit()
    db.refresh(rec)
    return {**_serialize_authority_record(rec), "rule_created": rule_created}


@router.post("/authority/records/{record_id}/reject", tags=["authority"])
def reject_authority_record(
    record_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Mark a candidate as rejected."""
    org_id = resolve_request_org_id(db, current_user)
    rec = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="AuthorityRecord not found")
    rec.status = "rejected"
    _audit(
        db, "authority.reject",
        user_id=current_user.id,
        entity_type="authority_record",
        entity_id=record_id,
    )
    db.commit()
    db.refresh(rec)
    return _serialize_authority_record(rec)


@router.delete("/authority/records/{record_id}", tags=["authority"])
def delete_authority_record(
    record_id: int = Path(ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Permanently delete an authority candidate record."""
    org_id = resolve_request_org_id(db, current_user)
    rec = get_scoped_record(db, models.AuthorityRecord, record_id, org_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="AuthorityRecord not found")
    db.delete(rec)
    db.commit()
    return {"message": "Deleted", "id": record_id}


@router.get("/authority/metrics", tags=["authority"])
def authority_metrics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Operational and quality KPIs for the Authority Resolution Layer."""
    org_id = resolve_request_org_id(db, current_user)
    total = (
        scope_query_to_org(db.query(func.count(models.AuthorityRecord.id)), models.AuthorityRecord, org_id)
        .scalar()
        or 0
    )

    by_status: dict = {}
    for row in (
        scope_query_to_org(
            db.query(models.AuthorityRecord.status, func.count(models.AuthorityRecord.id)),
            models.AuthorityRecord,
            org_id,
        )
        .group_by(models.AuthorityRecord.status)
        .all()
    ):
        by_status[row[0]] = row[1]

    by_resolution: dict = {}
    for row in (
        scope_query_to_org(
            db.query(models.AuthorityRecord.resolution_status, func.count(models.AuthorityRecord.id)),
            models.AuthorityRecord,
            org_id,
        )
        .group_by(models.AuthorityRecord.resolution_status)
        .all()
    ):
        if row[0]:
            by_resolution[row[0]] = row[1]

    by_source: dict = {}
    for row in (
        scope_query_to_org(
            db.query(models.AuthorityRecord.authority_source, func.count(models.AuthorityRecord.id)),
            models.AuthorityRecord,
            org_id,
        )
        .group_by(models.AuthorityRecord.authority_source)
        .all()
    ):
        by_source[row[0]] = row[1]

    avg_conf = (
        scope_query_to_org(db.query(func.avg(models.AuthorityRecord.confidence)), models.AuthorityRecord, org_id)
        .scalar()
        or 0.0
    )
    confirmed = by_status.get("confirmed", 0)
    rejected  = by_status.get("rejected", 0)

    return {
        "total_records":        total,
        "by_status":            by_status,
        "by_resolution_status": by_resolution,
        "by_source":            by_source,
        "avg_confidence":       round(float(avg_conf), 3),
        "confirm_rate":         round(confirmed / total, 3) if total > 0 else 0.0,
        "reject_rate":          round(rejected  / total, 3) if total > 0 else 0.0,
    }


# ── Authority field view (wildcard — must come LAST) ──────────────────────────

@router.get("/authority/{field}")
def get_authority_view(
    field: str,
    threshold: int = Query(default=80, ge=0, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = resolve_request_org_id(db, current_user)
    try:
        groups = _build_disambig_groups(field, threshold, db, org_id=org_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    rules = scope_query_to_org(
        db.query(models.NormalizationRule), models.NormalizationRule, org_id
    ).filter(
        models.NormalizationRule.field_name == field
    ).all()
    rules_by_original = {r.original_value: r.normalized_value for r in rules}

    annotated = []
    for g in groups:
        resolved_to = None
        has_rules = False
        for var in g["variations"]:
            if var in rules_by_original:
                has_rules = True
                resolved_to = rules_by_original[var]
                break
        annotated.append({**g, "has_rules": has_rules, "resolved_to": resolved_to})

    total_rules = (
        scope_query_to_org(
            db.query(func.count(models.NormalizationRule.id)), models.NormalizationRule, org_id
        )
        .filter(models.NormalizationRule.field_name == field)
        .scalar() or 0
    )

    return {
        "groups":        annotated,
        "total_groups":  len(annotated),
        "total_rules":   total_rules,
        "pending_groups": sum(1 for g in annotated if not g["has_rules"]),
    }
