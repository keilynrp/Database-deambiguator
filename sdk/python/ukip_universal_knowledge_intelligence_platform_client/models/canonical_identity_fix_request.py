from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CanonicalIdentityFixRequest")


@_attrs_define
class CanonicalIdentityFixRequest:
    """Inputs for canonical_id/entity_type backfill.

    Defaults bias toward safety: ``dry_run=True`` and both fields included.
    The operation is idempotent and never overwrites existing non-empty values.

        Attributes:
            dry_run (bool | Unset): If true, scan and report counters without committing changes. Default: True.
            limit (int | None | Unset): Cap the number of rows scanned. Omit for no cap.
            only (None | str | Unset): Limit the backfill to one field. Omit to repair both.
            org_id (int | None | Unset): Restrict to a single org id. Omit to scan all orgs.
    """

    dry_run: bool | Unset = True
    limit: int | None | Unset = UNSET
    only: None | str | Unset = UNSET
    org_id: int | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        dry_run = self.dry_run

        limit: int | None | Unset
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        only: None | str | Unset
        if isinstance(self.only, Unset):
            only = UNSET
        else:
            only = self.only

        org_id: int | None | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if dry_run is not UNSET:
            field_dict["dry_run"] = dry_run
        if limit is not UNSET:
            field_dict["limit"] = limit
        if only is not UNSET:
            field_dict["only"] = only
        if org_id is not UNSET:
            field_dict["org_id"] = org_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dry_run = d.pop("dry_run", UNSET)

        def _parse_limit(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        limit = _parse_limit(d.pop("limit", UNSET))

        def _parse_only(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        only = _parse_only(d.pop("only", UNSET))

        def _parse_org_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        canonical_identity_fix_request = cls(
            dry_run=dry_run,
            limit=limit,
            only=only,
            org_id=org_id,
        )

        return canonical_identity_fix_request
