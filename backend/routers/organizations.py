"""
Sprint 85 — Multi-tenancy: Organization management.
  POST   /organizations              — create (any authenticated user)
  GET    /organizations              — list orgs the current user belongs to
  GET    /organizations/{id}         — get org details (member+)
  PUT    /organizations/{id}         — update org (owner/admin)
  DELETE /organizations/{id}         — soft-delete (owner only)
  GET    /organizations/{id}/members — list members (member+)
  POST   /organizations/{id}/members — invite user by username (owner/admin)
  DELETE /organizations/{id}/members/{user_id} — remove member (owner/admin or self)
  POST   /organizations/{id}/switch  — switch current user's active org
"""
import json
import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from backend import models
from backend.auth import get_current_user
from backend.database import get_db
from backend.institutional_benchmarks import get_benchmark_profile
from backend.tenant_quotas import assert_org_quota_available, build_org_quota_snapshot

logger = logging.getLogger(__name__)
router = APIRouter(tags=["organizations"])

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]{1,98}[a-z0-9]$")


# ── Schemas ────────────────────────────────────────────────────────────────────

class OrgCreate(BaseModel):
    name:        str  = Field(..., min_length=2, max_length=200)
    slug:        str  = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    plan:        str  = Field("free", pattern="^(free|pro|enterprise)$")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not _SLUG_RE.match(v):
            raise ValueError("slug must be 3–100 lowercase alphanumeric chars or hyphens")
        return v


class OrgUpdate(BaseModel):
    name:        Optional[str]  = Field(None, min_length=2, max_length=200)
    description: Optional[str]  = Field(None, max_length=1000)
    plan:        Optional[str]   = Field(None, pattern="^(free|pro|enterprise)$")
    benchmark_profile_id: Optional[str] = Field(None, max_length=80)
    benchmark_profile_overrides: Optional[dict] = None


class InviteRequest(BaseModel):
    username: str = Field(..., min_length=1)
    role:     str = Field("member", pattern="^(admin|member)$")


def _serialize_org(org: models.Organization, member_count: int = 0) -> dict:
    try:
        benchmark_profile_overrides = json.loads(org.benchmark_profile_overrides) if org.benchmark_profile_overrides else {}
    except (TypeError, ValueError, json.JSONDecodeError):
        benchmark_profile_overrides = {}

    return {
        "id": org.id,
        "name": org.name,
        "slug": org.slug,
        "description": org.description,
        "plan": org.plan,
        "benchmark_profile_id": org.benchmark_profile_id,
        "benchmark_profile_overrides": benchmark_profile_overrides,
        "owner_id": org.owner_id,
        "is_active": org.is_active,
        "member_count": member_count,
        "created_at": org.created_at.isoformat() if org.created_at else None,
    }


def _serialize_member(m: models.OrganizationMember, user: models.User) -> dict:
    return {
        "user_id": m.user_id,
        "org_id": m.org_id,
        "role": m.role,
        "username": user.username,
        "display_name": getattr(user, "display_name", None) or user.username,
        "joined_at": m.joined_at.isoformat() if m.joined_at else None,
    }


def _get_org_or_404(org_id: int, db: Session) -> models.Organization:
    org = db.get(models.Organization, org_id)
    if not org or not org.is_active:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def _get_membership(org_id: int, user_id: int, db: Session) -> Optional[models.OrganizationMember]:
    return (
        db.query(models.OrganizationMember)
        .filter(models.OrganizationMember.org_id == org_id,
                models.OrganizationMember.user_id == user_id)
        .first()
    )


def _require_membership(org_id: int, user: models.User, db: Session,
                         min_role: str = "member") -> models.OrganizationMember:
    """Raises 403 if user is not a member (or not at min_role level)."""
    # super_admin can access all orgs
    if user.role == "super_admin":
        m = _get_membership(org_id, user.id, db)
        if m:
            return m
        # Return a synthetic membership for super_admin
        return models.OrganizationMember(org_id=org_id, user_id=user.id, role="owner")
    m = _get_membership(org_id, user.id, db)
    if not m:
        raise HTTPException(status_code=403, detail="You are not a member of this organization")
    role_rank = {"owner": 3, "admin": 2, "member": 1}
    if role_rank.get(m.role, 0) < role_rank.get(min_role, 0):
        raise HTTPException(status_code=403, detail=f"Role '{m.role}' is insufficient (need '{min_role}')")
    return m


# ── POST /organizations ────────────────────────────────────────────────────────

@router.post("/organizations", status_code=201, tags=["organizations"])
def create_organization(
    payload: OrgCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new organization; caller becomes the owner."""
    if db.query(models.Organization).filter(models.Organization.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="Slug already taken")
    org = models.Organization(
        name=payload.name,
        slug=payload.slug,
        description=payload.description,
        plan=payload.plan,
        owner_id=current_user.id,
    )
    db.add(org)
    db.flush()
    # Add creator as owner member
    db.add(models.OrganizationMember(org_id=org.id, user_id=current_user.id, role="owner"))
    # Set as current user's active org if they have none
    if not getattr(current_user, "org_id", None):
        current_user.org_id = org.id
    db.commit()
    db.refresh(org)
    logger.info("Organization '%s' created by user %d", org.slug, current_user.id)
    return _serialize_org(org, member_count=1)


# ── GET /organizations ─────────────────────────────────────────────────────────

@router.get("/organizations", tags=["organizations"])
def list_organizations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List organizations the current user belongs to (super_admin sees all)."""
    if current_user.role == "super_admin":
        orgs = db.query(models.Organization).filter(models.Organization.is_active == True).all()
    else:
        memberships = (
            db.query(models.OrganizationMember)
            .filter(models.OrganizationMember.user_id == current_user.id)
            .all()
        )
        org_ids = [m.org_id for m in memberships]
        orgs = db.query(models.Organization).filter(
            models.Organization.id.in_(org_ids),
            models.Organization.is_active == True,
        ).all()
    result = []
    for org in orgs:
        count = db.query(models.OrganizationMember).filter(
            models.OrganizationMember.org_id == org.id
        ).count()
        result.append(_serialize_org(org, member_count=count))
    return result


# ── GET /organizations/{id} ────────────────────────────────────────────────────

@router.get("/organizations/{org_id}", tags=["organizations"])
def get_organization(
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org = _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db)
    count = db.query(models.OrganizationMember).filter(
        models.OrganizationMember.org_id == org.id
    ).count()
    return _serialize_org(org, member_count=count)


@router.get("/organizations/{org_id}/quotas", tags=["organizations"])
def get_organization_quotas(
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org = _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db)
    return build_org_quota_snapshot(db, org, current_user=current_user)


# ── PUT /organizations/{id} ────────────────────────────────────────────────────

@router.put("/organizations/{org_id}", tags=["organizations"])
def update_organization(
    payload: OrgUpdate,
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org = _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db, min_role="admin")
    if payload.name is not None:
        org.name = payload.name
    if payload.description is not None:
        org.description = payload.description
    if payload.plan is not None:
        org.plan = payload.plan
    if payload.benchmark_profile_id is not None:
        if payload.benchmark_profile_id and not get_benchmark_profile(payload.benchmark_profile_id):
            raise HTTPException(status_code=422, detail="Unknown benchmark profile")
        org.benchmark_profile_id = payload.benchmark_profile_id or None
    if payload.benchmark_profile_overrides is not None:
        org.benchmark_profile_overrides = json.dumps(payload.benchmark_profile_overrides)
    db.commit()
    db.refresh(org)
    return _serialize_org(org)


# ── DELETE /organizations/{id} ─────────────────────────────────────────────────

@router.delete("/organizations/{org_id}", tags=["organizations"])
def delete_organization(
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org = _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db, min_role="owner")
    org.is_active = False
    db.commit()
    logger.info("Organization %d soft-deleted by user %d", org_id, current_user.id)
    return {"deleted": org_id}


# ── GET /organizations/{id}/members ───────────────────────────────────────────

@router.get("/organizations/{org_id}/members", tags=["organizations"])
def list_members(
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db)
    memberships = (
        db.query(models.OrganizationMember)
        .filter(models.OrganizationMember.org_id == org_id)
        .all()
    )
    result = []
    for m in memberships:
        user = db.get(models.User, m.user_id)
        if user:
            result.append(_serialize_member(m, user))
    return result


# ── POST /organizations/{id}/members ──────────────────────────────────────────

@router.post("/organizations/{org_id}/members", status_code=201, tags=["organizations"])
def invite_member(
    payload: InviteRequest,
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db, min_role="admin")
    target = db.query(models.User).filter(models.User.username == payload.username).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if _get_membership(org_id, target.id, db):
        raise HTTPException(status_code=409, detail="User is already a member")
    assert_org_quota_available(db, org_id, "members", current_user=current_user)
    m = models.OrganizationMember(org_id=org_id, user_id=target.id, role=payload.role)
    db.add(m)
    db.commit()
    db.refresh(m)
    return _serialize_member(m, target)


# ── DELETE /organizations/{id}/members/{user_id} ──────────────────────────────

@router.delete("/organizations/{org_id}/members/{member_user_id}", tags=["organizations"])
def remove_member(
    org_id: int = Path(..., ge=1),
    member_user_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    _get_org_or_404(org_id, db)
    caller_m = _require_membership(org_id, current_user, db, min_role="admin")
    # Allow self-removal at any role
    if member_user_id != current_user.id:
        if caller_m.role not in ("owner", "admin"):
            raise HTTPException(status_code=403, detail="Insufficient role to remove others")
    target_m = _get_membership(org_id, member_user_id, db)
    if not target_m:
        raise HTTPException(status_code=404, detail="Member not found")
    if target_m.role == "owner" and member_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot remove the organization owner")
    db.delete(target_m)
    db.commit()
    return {"removed": member_user_id, "org_id": org_id}


# ── POST /organizations/{id}/switch ───────────────────────────────────────────

@router.post("/organizations/{org_id}/switch", tags=["organizations"])
def switch_organization(
    org_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Set the caller's active organization context."""
    _get_org_or_404(org_id, db)
    _require_membership(org_id, current_user, db)
    current_user.org_id = org_id
    db.commit()
    return {"active_org_id": org_id}
