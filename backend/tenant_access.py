from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Query, Session

from backend import models

_ACTIVE_ORG_REQUIRED_DETAIL = "Active organization required for tenant-scoped resource"
LEGACY_GLOBAL_ORG_ID = -1


def resolve_request_org_id(
    db: Session,
    current_user: models.User,
    *,
    allow_super_admin_global: bool = True,
    allow_legacy_global: bool = True,
) -> int | None:
    org_id = getattr(current_user, "org_id", None)

    if org_id is None:
        if current_user.role == "super_admin" and allow_super_admin_global:
            return None
        if allow_legacy_global:
            return LEGACY_GLOBAL_ORG_ID
        raise HTTPException(status_code=409, detail=_ACTIVE_ORG_REQUIRED_DETAIL)

    org = (
        db.query(models.Organization)
        .filter(
            models.Organization.id == org_id,
            models.Organization.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not org:
        raise HTTPException(status_code=404, detail="Active organization not found")

    if current_user.role != "super_admin":
        membership = (
            db.query(models.OrganizationMember)
            .filter(
                models.OrganizationMember.org_id == org_id,
                models.OrganizationMember.user_id == current_user.id,
            )
            .first()
        )
        if not membership:
            raise HTTPException(
                status_code=403,
                detail="You are not a member of the active organization",
            )

    return org_id


def is_legacy_global_scope(org_id: int | None) -> bool:
    return org_id == LEGACY_GLOBAL_ORG_ID


def org_scope_filter(org_column, org_id: int | None):
    if org_id is None:
        return None
    if is_legacy_global_scope(org_id):
        return org_column.is_(None)
    return org_column == org_id


def add_org_sql_filter(
    where_clauses: list[str],
    params: dict[str, object],
    org_id: int | None,
    *,
    column_name: str = "org_id",
) -> None:
    if org_id is None:
        return
    if is_legacy_global_scope(org_id):
        where_clauses.append(f"{column_name} IS NULL")
        return
    where_clauses.append(f"{column_name} = :org_id")
    params["org_id"] = org_id


def persisted_org_id(org_id: int | None) -> int | None:
    if is_legacy_global_scope(org_id):
        return None
    return org_id


def scope_query_to_org(query: Query, model, org_id: int | None) -> Query:
    org_column = getattr(model, "org_id", None)
    if org_id is None:
        return query
    if org_column is None:
        raise ValueError(f"Model {model!r} does not expose org_id")
    condition = org_scope_filter(org_column, org_id)
    if condition is None:
        return query
    return query.filter(condition)


def get_scoped_record(
    db: Session,
    model,
    record_id: int,
    org_id: int | None,
):
    return (
        scope_query_to_org(db.query(model), model, org_id)
        .filter(model.id == record_id)
        .first()
    )


def scope_tag(org_id: int | None) -> str:
    if org_id is None:
        return "global"
    if is_legacy_global_scope(org_id):
        return "legacy_global"
    return f"org_{org_id}"
