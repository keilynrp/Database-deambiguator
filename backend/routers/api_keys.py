"""
Sprint 82 — Public API Keys: long-lived keys for programmatic access.

Key format:  ukip_<32 random url-safe base64 chars>
Storage:     Only key_prefix (first 16 chars) + SHA-256 hash stored — never the full key.
Auth:        Bearer token support: if token starts with 'ukip_' → look up in api_keys table.

Endpoints:
  GET    /api-keys            — list caller's keys (shows prefix, never full key)
  POST   /api-keys            — create key (returns full key ONCE, never again)
  DELETE /api-keys/{id}       — revoke key
  GET    /api-keys/scopes     — available scope definitions
"""
import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(tags=["api-keys"])

_ALL_SCOPES = ["read", "write", "admin"]

# ── Key generation ────────────────────────────────────────────────────────────

def _generate_key() -> tuple[str, str, str]:
    """
    Returns (full_key, prefix, sha256_hash).
    full_key:  'ukip_' + 40 url-safe random chars (shown once at creation)
    prefix:    first 16 chars of full_key  (shown in listings for identification)
    hash:      SHA-256 hex of full_key  (stored in DB for verification)
    """
    rand = secrets.token_urlsafe(30)  # 30 bytes → ~40 chars
    full_key = f"ukip_{rand}"
    prefix = full_key[:16]
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, prefix, key_hash


def verify_api_key(raw_key: str, db: Session) -> Optional[models.ApiKey]:
    """
    Look up an API key by hash. Updates last_used_at.
    Returns the ApiKey record if valid and active, None otherwise.
    """
    if not raw_key.startswith("ukip_"):
        return None
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_record = (
        db.query(models.ApiKey)
        .filter(
            models.ApiKey.key_hash == key_hash,
            models.ApiKey.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not key_record:
        return None
    if key_record.expires_at and key_record.expires_at < datetime.now(timezone.utc):
        return None
    key_record.last_used_at = datetime.now(timezone.utc)
    try:
        db.commit()
    except Exception:
        pass
    return key_record


# ── Schemas ───────────────────────────────────────────────────────────────────

class ApiKeyCreate(BaseModel):
    name:       str            = Field(min_length=1, max_length=200)
    scopes:     List[str]      = Field(default=["read"])
    expires_days: Optional[int] = Field(default=None, ge=1, le=3650)


# ── Serializer ────────────────────────────────────────────────────────────────

def _serialize(k: models.ApiKey, full_key: Optional[str] = None) -> dict:
    d = {
        "id":           k.id,
        "name":         k.name,
        "key_prefix":   k.key_prefix,
        "scopes":       json.loads(k.scopes) if k.scopes else ["read"],
        "is_active":    k.is_active,
        "expires_at":   k.expires_at.isoformat() if k.expires_at else None,
        "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
        "created_at":   k.created_at.isoformat() if k.created_at else None,
    }
    if full_key:
        d["key"] = full_key   # only present at creation
    return d


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/api-keys/scopes", tags=["api-keys"])
def list_scopes(_: models.User = Depends(get_current_user)):
    return [
        {"id": "read",  "label": "Read",  "description": "GET endpoints: entities, analytics, reports"},
        {"id": "write", "label": "Write", "description": "Mutating endpoints: upload, edit entities, rules"},
        {"id": "admin", "label": "Admin", "description": "Store integrations, AI config, user management"},
    ]


@router.get("/api-keys", tags=["api-keys"])
def list_api_keys(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    keys = (
        db.query(models.ApiKey)
        .filter(models.ApiKey.user_id == current_user.id)
        .order_by(models.ApiKey.id.desc())
        .all()
    )
    return [_serialize(k) for k in keys]


@router.post("/api-keys", status_code=201, tags=["api-keys"])
def create_api_key(
    payload: ApiKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    invalid = [s for s in payload.scopes if s not in _ALL_SCOPES]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid scopes: {invalid}. Valid: {_ALL_SCOPES}",
        )
    if not payload.scopes:
        raise HTTPException(status_code=422, detail="At least one scope is required")

    full_key, prefix, key_hash = _generate_key()

    expires_at = None
    if payload.expires_days:
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=payload.expires_days)

    key_record = models.ApiKey(
        user_id=current_user.id,
        name=payload.name.strip(),
        key_prefix=prefix,
        key_hash=key_hash,
        scopes=json.dumps(payload.scopes),
        expires_at=expires_at,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )
    db.add(key_record)
    db.commit()
    db.refresh(key_record)
    logger.info("API key '%s' created for user %d (prefix=%s)", payload.name, current_user.id, prefix)
    return _serialize(key_record, full_key=full_key)


@router.delete("/api-keys/{key_id}", tags=["api-keys"])
def revoke_api_key(
    key_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    key_record = db.get(models.ApiKey, key_id)
    if not key_record or key_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="API key not found")
    key_record.is_active = False
    db.commit()
    logger.info("API key %d revoked by user %d", key_id, current_user.id)
    return {"revoked": key_id}
