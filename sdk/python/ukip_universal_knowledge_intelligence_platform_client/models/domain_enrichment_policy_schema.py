from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainEnrichmentPolicySchema")


@_attrs_define
class DomainEnrichmentPolicySchema:
    """Response schema for a DomainEnrichmentPolicy row.

    Attributes:
        domain_id (str):
        enabled (bool):
        id (int):
        max_budget_per_run (int):
        min_enrichment_pct (float):
        staleness_threshold_days (int):
        created_at (datetime.datetime | None | Unset):
        updated_at (datetime.datetime | None | Unset):
    """

    domain_id: str
    enabled: bool
    id: int
    max_budget_per_run: int
    min_enrichment_pct: float
    staleness_threshold_days: int
    created_at: datetime.datetime | None | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        enabled = self.enabled

        id = self.id

        max_budget_per_run = self.max_budget_per_run

        min_enrichment_pct = self.min_enrichment_pct

        staleness_threshold_days = self.staleness_threshold_days

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "enabled": enabled,
                "id": id,
                "max_budget_per_run": max_budget_per_run,
                "min_enrichment_pct": min_enrichment_pct,
                "staleness_threshold_days": staleness_threshold_days,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        enabled = d.pop("enabled")

        id = d.pop("id")

        max_budget_per_run = d.pop("max_budget_per_run")

        min_enrichment_pct = d.pop("min_enrichment_pct")

        staleness_threshold_days = d.pop("staleness_threshold_days")

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = datetime.datetime.fromisoformat(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = datetime.datetime.fromisoformat(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        domain_enrichment_policy_schema = cls(
            domain_id=domain_id,
            enabled=enabled,
            id=id,
            max_budget_per_run=max_budget_per_run,
            min_enrichment_pct=min_enrichment_pct,
            staleness_threshold_days=staleness_threshold_days,
            created_at=created_at,
            updated_at=updated_at,
        )

        domain_enrichment_policy_schema.additional_properties = d
        return domain_enrichment_policy_schema

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
