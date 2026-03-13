"""
Phase 11 — Context Engineering Layer
  GET  /context/snapshot/{domain_id}   — live domain context (not persisted)
  GET  /context/sessions               — list saved sessions
  POST /context/sessions               — save a new session  (201)
  DELETE /context/sessions/{id}        — delete a session    (204)
  GET  /context/tools                  — list available tools
  POST /context/invoke                 — invoke a tool by name
"""
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_current_user, require_role
from backend.context_engine import ContextEngine
from backend.database import get_db
from backend.schema_registry import SchemaRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/context", tags=["context"])

_engine = ContextEngine()


# ── Helper ─────────────────────────────────────────────────────────────────────

def _validate_domain(domain_id: str) -> None:
    if SchemaRegistry().get_domain(domain_id) is None:
        raise HTTPException(status_code=404, detail=f"Domain '{domain_id}' not found")


# ── Snapshot (live, not persisted) ─────────────────────────────────────────────

@router.get("/snapshot/{domain_id}")
def get_snapshot(
    domain_id: str,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Return a live domain context snapshot (not saved to DB)."""
    _validate_domain(domain_id)
    return _engine.build_domain_context(domain_id, db)


# ── Saved sessions ─────────────────────────────────────────────────────────────

@router.get("/sessions")
def list_sessions(
    domain_id: str | None = None,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """List all saved analysis context sessions, optionally filtered by domain."""
    q = db.query(models.AnalysisContext).order_by(models.AnalysisContext.created_at.desc())
    if domain_id:
        q = q.filter(models.AnalysisContext.domain_id == domain_id)
    return q.limit(100).all()


@router.post("/sessions", status_code=201)
def create_session(
    payload: schemas.AnalysisContextCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Build and persist a domain context snapshot as a named session."""
    _validate_domain(payload.domain_id)
    ctx = _engine.build_domain_context(payload.domain_id, db)
    record = models.AnalysisContext(
        domain_id=payload.domain_id,
        user_id=current_user.id,
        label=payload.label or f"Snapshot {ctx['generated_at'][:10]}",
        context_snapshot=_engine.snapshot_json(ctx),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """Delete a saved session."""
    record = db.get(models.AnalysisContext, session_id)
    if not record:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(record)
    db.commit()


# ── Tool Registry endpoints ─────────────────────────────────────────────────────

@router.get("/tools")
def list_tools(_: models.User = Depends(get_current_user)):
    """Return the list of available context tools."""
    from backend.tool_registry import get_registry
    return get_registry().list_tools()


@router.post("/invoke")
def invoke_tool(
    payload: dict,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_role("super_admin", "admin", "editor")),
):
    """
    Invoke a registered tool by name.
    Body: {"tool": "<name>", "params": {...}}
    """
    from backend.tool_registry import get_registry
    tool_name = payload.get("tool")
    params    = payload.get("params", {})
    if not tool_name:
        raise HTTPException(status_code=422, detail="'tool' field is required")
    registry = get_registry()
    try:
        result = registry.invoke(tool_name, params, db)
        return {"tool": tool_name, "result": result}
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found. Available: {[t['name'] for t in registry.list_tools()]}",
        )
    except Exception as exc:
        logger.error("Tool invocation error [%s]: %s", tool_name, exc)
        raise HTTPException(status_code=500, detail=str(exc))
