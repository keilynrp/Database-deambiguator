from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainEnrichmentPolicyUpdate")


@_attrs_define
class DomainEnrichmentPolicyUpdate:
    """Request body for creating or updating a DomainEnrichmentPolicy.

    Attributes:
        enabled (bool | None | Unset):
        max_budget_per_run (int | None | Unset):
        min_enrichment_pct (float | None | Unset):
        staleness_threshold_days (int | None | Unset):
    """

    enabled: bool | None | Unset = UNSET
    max_budget_per_run: int | None | Unset = UNSET
    min_enrichment_pct: float | None | Unset = UNSET
    staleness_threshold_days: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        max_budget_per_run: int | None | Unset
        if isinstance(self.max_budget_per_run, Unset):
            max_budget_per_run = UNSET
        else:
            max_budget_per_run = self.max_budget_per_run

        min_enrichment_pct: float | None | Unset
        if isinstance(self.min_enrichment_pct, Unset):
            min_enrichment_pct = UNSET
        else:
            min_enrichment_pct = self.min_enrichment_pct

        staleness_threshold_days: int | None | Unset
        if isinstance(self.staleness_threshold_days, Unset):
            staleness_threshold_days = UNSET
        else:
            staleness_threshold_days = self.staleness_threshold_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if max_budget_per_run is not UNSET:
            field_dict["max_budget_per_run"] = max_budget_per_run
        if min_enrichment_pct is not UNSET:
            field_dict["min_enrichment_pct"] = min_enrichment_pct
        if staleness_threshold_days is not UNSET:
            field_dict["staleness_threshold_days"] = staleness_threshold_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_max_budget_per_run(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_budget_per_run = _parse_max_budget_per_run(d.pop("max_budget_per_run", UNSET))

        def _parse_min_enrichment_pct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_enrichment_pct = _parse_min_enrichment_pct(d.pop("min_enrichment_pct", UNSET))

        def _parse_staleness_threshold_days(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        staleness_threshold_days = _parse_staleness_threshold_days(d.pop("staleness_threshold_days", UNSET))

        domain_enrichment_policy_update = cls(
            enabled=enabled,
            max_budget_per_run=max_budget_per_run,
            min_enrichment_pct=min_enrichment_pct,
            staleness_threshold_days=staleness_threshold_days,
        )

        domain_enrichment_policy_update.additional_properties = d
        return domain_enrichment_policy_update

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
