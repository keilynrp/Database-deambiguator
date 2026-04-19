"""
Notifications endpoints.

Sprint 43 — Email Notification Settings:
  GET    /notifications/settings           — admin+
  PUT    /notifications/settings           — admin+
  POST   /notifications/test               — admin+ (sends test email)

Sprint 56 — Notification Center:
  GET    /notifications/center             — paginated feed with is_read (any auth)
  GET    /notifications/center/unread-count — fast unread badge count (any auth)
  POST   /notifications/center/read-all    — mark all read for current user (any auth)
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import not_
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user, require_role
from backend.database import get_db
from backend.notifications.email_sender import send_notification

logger = logging.getLogger(__name__)

router = APIRouter(tags=["notifications"])

# ── Action metadata (shared with feed) ────────────────────────────────────────

_ACTION_ICONS: dict[str, str] = {
    "upload":              "📥",
    "entity.update":       "✏️",
    "entity.delete":       "🗑️",
    "entity.bulk_delete":  "🗑️",
    "harmonization.apply": "⚙️",
    "authority.confirm":   "✅",
    "authority.reject":    "❌",
    "entity.merge":        "🔗",
    "pull":                "📥",
    "scheduled_pull":      "🗓️",
}

_ACTION_LABELS: dict[str, str] = {
    "upload":              "File uploaded",
    "entity.update":       "Entity updated",
    "entity.delete":       "Entity deleted",
    "entity.bulk_delete":  "Entities bulk-deleted",
    "harmonization.apply": "Harmonization applied",
    "authority.confirm":   "Authority record confirmed",
    "authority.reject":    "Authority record rejected",
    "entity.merge":        "Entities merged",
    "pull":                "Store pull completed",
    "scheduled_pull":      "Scheduled import completed",
}

_RESOURCE_LABELS: dict[str, str] = {
    "entity": "Entity",
    "rule": "Rule",
    "report": "Report",
    "export": "Export",
    "artifact": "Artifact",
    "context": "Context snapshot",
    "store": "Store connection",
    "ai_integration": "AI integration",
    "authority": "Authority record",
    "harmonization": "Harmonization workflow",
    "disambiguation": "Disambiguation record",
    "domain": "Domain",
    "user": "User",
    "annotation": "Annotation",
    "rag": "RAG configuration",
    "demo": "Demo asset",
    "branding": "Branding setting",
    "olap": "OLAP view",
    "analyzer": "Analyzer result",
    "webhook": "Webhook",
    "notification": "Notification setting",
    "enrichment": "Enrichment job",
    "ingest": "Import job",
}

_GENERIC_ACTION_LABELS: dict[str, str] = {
    "CREATE": "created",
    "UPDATE": "updated",
    "DELETE": "deleted",
}

_GENERIC_ACTION_ICONS: dict[str, str] = {
    "CREATE": "🆕",
    "UPDATE": "✏️",
    "DELETE": "🗑️",
}

# Map action → frontend href template (None = no link)
_ACTION_HREF: dict[str, str | None] = {
    "upload":              "/import-export",
    "entity.update":       "/entities/{entity_id}",
    "entity.delete":       None,
    "entity.bulk_delete":  "/",
    "harmonization.apply": "/harmonization",
    "authority.confirm":   "/authority",
    "authority.reject":    "/authority",
    "entity.merge":        "/entities/{entity_id}",
}


def _build_href(action: str, entity_id: int | None) -> str | None:
    template = _ACTION_HREF.get(action)
    if not template:
        return None
    if "{entity_id}" in template and entity_id:
        return template.replace("{entity_id}", str(entity_id))
    return template.replace("{entity_id}", "") if "{entity_id}" in template else template


def _humanize_action_label(action: str | None, entity_type: str | None) -> str:
    if not action:
        return ""
    known = _ACTION_LABELS.get(action)
    if known:
        return known
    generic_verb = _GENERIC_ACTION_LABELS.get(action.upper())
    if generic_verb:
        resource = _RESOURCE_LABELS.get(entity_type or "", "Record")
        return f"{resource} {generic_verb}"
    return action.replace("_", " ").replace(".", " ").strip().title()


def _icon_for_action(action: str | None) -> str:
    if not action:
        return "📋"
    return _ACTION_ICONS.get(action, _GENERIC_ACTION_ICONS.get(action.upper(), "📋"))


def _serialize_entry(
    entry: models.AuditLog,
    last_read_at: datetime | None,
    individually_read_ids: set[int] | None = None,
) -> dict:
    individually_read_ids = individually_read_ids or set()
    is_read = (
        entry.id in individually_read_ids
        or (
            last_read_at is not None
            and entry.created_at is not None
            and entry.created_at <= last_read_at
        )
    )
    details = None
    if entry.details:
        try:
            details = json.loads(entry.details)
        except Exception:
            details = None
    return {
        "id":           entry.id,
        "action":       entry.action,
        "label":        _humanize_action_label(entry.action, entry.entity_type),
        "icon":         _icon_for_action(entry.action),
        "entity_type":  entry.entity_type,
        "entity_id":    entry.entity_id,
        "username":     entry.username,
        "details":      details,
        "href":         _build_href(entry.action, entry.entity_id),
        "created_at":   entry.created_at.isoformat() if entry.created_at else None,
        "is_read":      is_read,
    }


def _get_or_create_settings(db: Session) -> models.NotificationSettings:
    try:
        s = db.get(models.NotificationSettings, 1)
    except (OperationalError, ProgrammingError):
        db.rollback()
        models.NotificationSettings.__table__.create(bind=db.get_bind(), checkfirst=True)
        s = db.get(models.NotificationSettings, 1)
    if not s:
        s = models.NotificationSettings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def _encrypt_password(plain: str) -> str:
    """Encrypt SMTP password using the Fernet key, if available."""
    if not plain:
        return ""
    try:
        from backend.encryption import encrypt_value
        return encrypt_value(plain)
    except Exception:
        logger.warning("Could not encrypt SMTP password; storing as-is")
        return plain


# ── GET /notifications/settings ───────────────────────────────────────────────

@router.get("/notifications/settings", tags=["notifications"])
def get_notification_settings(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role("super_admin", "admin")),
):
    s = _get_or_create_settings(db)
    return schemas.NotificationSettingsResponse.model_validate(s)


# ── PUT /notifications/settings ───────────────────────────────────────────────

@router.put("/notifications/settings", tags=["notifications"])
def update_notification_settings(
    payload: schemas.NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role("super_admin", "admin")),
):
    s = _get_or_create_settings(db)
    data = payload.model_dump(exclude_unset=True)

    if "smtp_password" in data:
        plain = data.pop("smtp_password")
        if plain:
            s.smtp_password = _encrypt_password(plain)
    for field, value in data.items():
        setattr(s, field, value)

    db.commit()
    db.refresh(s)
    return schemas.NotificationSettingsResponse.model_validate(s)


# ── POST /notifications/test ──────────────────────────────────────────────────

@router.post("/notifications/test", tags=["notifications"])
def test_notification(
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role("super_admin", "admin")),
):
    s = _get_or_create_settings(db)
    sent = send_notification(
        s,
        subject="UKIP: Test Notification",
        body="This is a test email from the UKIP platform. If you received this, your SMTP settings are working correctly.",
    )
    return {"sent": sent}


# ── Sprint 56: Notification Center ────────────────────────────────────────────

def _get_user_state(db: Session, user_id: int) -> models.UserNotificationState:
    state = db.get(models.UserNotificationState, user_id)
    if not state:
        state = models.UserNotificationState(user_id=user_id, last_read_at=None)
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def _read_ids_subquery(db: Session, user_id: int):
    return (
        db.query(models.UserNotificationRead.audit_log_id)
        .filter(models.UserNotificationRead.user_id == user_id)
    )


def _get_individually_read_ids(
    db: Session,
    user_id: int,
    entry_ids: list[int],
) -> set[int]:
    if not entry_ids:
        return set()
    rows = (
        db.query(models.UserNotificationRead.audit_log_id)
        .filter(models.UserNotificationRead.user_id == user_id)
        .filter(models.UserNotificationRead.audit_log_id.in_(entry_ids))
        .all()
    )
    return {row[0] for row in rows}


@router.get("/notifications/center", tags=["notifications"])
def get_notification_center(
    skip:   int           = Query(default=0,   ge=0),
    limit:  int           = Query(default=50,  ge=1, le=200),
    action: Optional[str] = Query(default=None),
    db:     Session       = Depends(get_db),
    user:   models.User   = Depends(get_current_user),
):
    """
    Paginated notification feed (newest first) with per-entry is_read flag.
    Available to any authenticated user.
    """
    state = _get_user_state(db, user.id)

    q = db.query(models.AuditLog)
    if action:
        q = q.filter(models.AuditLog.action == action)

    total = q.count()

    # Unread count: entries created after last_read_at
    unread_count: int
    unread_q = q.filter(not_(models.AuditLog.id.in_(_read_ids_subquery(db, user.id))))
    if state.last_read_at is None:
        unread_count = unread_q.count()
    else:
        unread_count = unread_q.filter(models.AuditLog.created_at > state.last_read_at).count()

    items = (
        q.order_by(models.AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    individually_read_ids = _get_individually_read_ids(db, user.id, [e.id for e in items])

    return {
        "total":        total,
        "unread_count": unread_count,
        "skip":         skip,
        "limit":        limit,
        "last_read_at": state.last_read_at.isoformat() if state.last_read_at else None,
        "items":        [_serialize_entry(e, state.last_read_at, individually_read_ids) for e in items],
    }


@router.get("/notifications/center/unread-count", tags=["notifications"])
def get_unread_count(
    db:   Session     = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Fast unread count for the bell badge."""
    state = _get_user_state(db, user.id)
    q = db.query(models.AuditLog).filter(not_(models.AuditLog.id.in_(_read_ids_subquery(db, user.id))))
    if state.last_read_at is None:
        count = q.count()
    else:
        count = q.filter(models.AuditLog.created_at > state.last_read_at).count()
    return {"unread_count": count}


@router.post("/notifications/center/read-all", tags=["notifications"])
def mark_all_read(
    db:   Session     = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Set the current user's last_read_at to now, marking all notifications read."""
    state = _get_user_state(db, user.id)
    # Store as naive UTC to match the format SQLite uses for created_at columns
    state.last_read_at = datetime.now(timezone.utc).replace(tzinfo=None)
    (
        db.query(models.UserNotificationRead)
        .filter(models.UserNotificationRead.user_id == user.id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {
        "ok":           True,
        "last_read_at": state.last_read_at.isoformat() + "Z",
    }


@router.post("/notifications/center/read/{entry_id}", tags=["notifications"])
def mark_notification_read(
    entry_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Mark a single notification as read for the current user."""
    entry = db.get(models.AuditLog, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Notification not found")

    state = _get_user_state(db, user.id)
    if (
        state.last_read_at is not None
        and entry.created_at is not None
        and entry.created_at <= state.last_read_at
    ):
        return {"ok": True, "entry_id": entry_id, "already_read": True}

    existing = (
        db.query(models.UserNotificationRead)
        .filter(models.UserNotificationRead.user_id == user.id)
        .filter(models.UserNotificationRead.audit_log_id == entry_id)
        .first()
    )
    if not existing:
        db.add(models.UserNotificationRead(user_id=user.id, audit_log_id=entry_id))
        db.commit()

    return {"ok": True, "entry_id": entry_id, "already_read": False}
