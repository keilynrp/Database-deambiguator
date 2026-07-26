from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="LegacyAffiliationFixRequest")


@_attrs_define
class LegacyAffiliationFixRequest:
    """Inputs for the legacy-affiliation backfill.

    Defaults bias toward safety: ``dry_run=True`` and no re-enrichment.
    Callers must explicitly opt out of dry-run to mutate the database.

        Attributes:
            dry_run (bool | Unset): If true, scan and report counters without committing changes. Defaults to true so
                unprivileged misuse cannot mutate data. Default: True.
            limit (int | None | Unset): Cap the number of rows scanned. Omit for no cap.
            org_id (int | None | Unset): Restrict to a single org id. Omit to scan all orgs.
            requeue_enrichment (bool | Unset): If true, mark fixed entities with enrichment_status='pending' so the worker
                repopulates affiliation from canonical institutions. Default: False.
    """

    dry_run: bool | Unset = True
    limit: int | None | Unset = UNSET
    org_id: int | None | Unset = UNSET
    requeue_enrichment: bool | Unset = False

    def to_dict(self) -> dict[str, Any]:
        dry_run = self.dry_run

        limit: int | None | Unset
        if isinstance(self.limit, Unset):
            limit = UNSET
        else:
            limit = self.limit

        org_id: int | None | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        requeue_enrichment = self.requeue_enrichment

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if dry_run is not UNSET:
            field_dict["dry_run"] = dry_run
        if limit is not UNSET:
            field_dict["limit"] = limit
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if requeue_enrichment is not UNSET:
            field_dict["requeue_enrichment"] = requeue_enrichment

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

        def _parse_org_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        requeue_enrichment = d.pop("requeue_enrichment", UNSET)

        legacy_affiliation_fix_request = cls(
            dry_run=dry_run,
            limit=limit,
            org_id=org_id,
            requeue_enrichment=requeue_enrichment,
        )

        return legacy_affiliation_fix_request
