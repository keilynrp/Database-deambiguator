from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalMetricResponse")


@_attrs_define
class JournalMetricResponse:
    """
    Attributes:
        issn_l (str):
        apc_currency (None | str | Unset):
        apc_source (None | str | Unset):
        apc_usd (int | None | Unset):
        display_name (None | str | Unset):
        h_index (int | None | Unset):
        if_metric_kind (None | str | Unset):
        is_in_doaj (bool | None | Unset):
        nif_bayes (float | None | Unset):
        nif_ci_high (float | None | Unset):
        nif_ci_low (float | None | Unset):
        nif_field (None | str | Unset):
        nif_updated_at (datetime.datetime | None | Unset):
        normalized_impact_factor (float | None | Unset):
        source_id (None | str | Unset):
        two_yr_mean_citedness (float | None | Unset):
        works_count (int | None | Unset):
    """

    issn_l: str
    apc_currency: None | str | Unset = UNSET
    apc_source: None | str | Unset = UNSET
    apc_usd: int | None | Unset = UNSET
    display_name: None | str | Unset = UNSET
    h_index: int | None | Unset = UNSET
    if_metric_kind: None | str | Unset = UNSET
    is_in_doaj: bool | None | Unset = UNSET
    nif_bayes: float | None | Unset = UNSET
    nif_ci_high: float | None | Unset = UNSET
    nif_ci_low: float | None | Unset = UNSET
    nif_field: None | str | Unset = UNSET
    nif_updated_at: datetime.datetime | None | Unset = UNSET
    normalized_impact_factor: float | None | Unset = UNSET
    source_id: None | str | Unset = UNSET
    two_yr_mean_citedness: float | None | Unset = UNSET
    works_count: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issn_l = self.issn_l

        apc_currency: None | str | Unset
        if isinstance(self.apc_currency, Unset):
            apc_currency = UNSET
        else:
            apc_currency = self.apc_currency

        apc_source: None | str | Unset
        if isinstance(self.apc_source, Unset):
            apc_source = UNSET
        else:
            apc_source = self.apc_source

        apc_usd: int | None | Unset
        if isinstance(self.apc_usd, Unset):
            apc_usd = UNSET
        else:
            apc_usd = self.apc_usd

        display_name: None | str | Unset
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        h_index: int | None | Unset
        if isinstance(self.h_index, Unset):
            h_index = UNSET
        else:
            h_index = self.h_index

        if_metric_kind: None | str | Unset
        if isinstance(self.if_metric_kind, Unset):
            if_metric_kind = UNSET
        else:
            if_metric_kind = self.if_metric_kind

        is_in_doaj: bool | None | Unset
        if isinstance(self.is_in_doaj, Unset):
            is_in_doaj = UNSET
        else:
            is_in_doaj = self.is_in_doaj

        nif_bayes: float | None | Unset
        if isinstance(self.nif_bayes, Unset):
            nif_bayes = UNSET
        else:
            nif_bayes = self.nif_bayes

        nif_ci_high: float | None | Unset
        if isinstance(self.nif_ci_high, Unset):
            nif_ci_high = UNSET
        else:
            nif_ci_high = self.nif_ci_high

        nif_ci_low: float | None | Unset
        if isinstance(self.nif_ci_low, Unset):
            nif_ci_low = UNSET
        else:
            nif_ci_low = self.nif_ci_low

        nif_field: None | str | Unset
        if isinstance(self.nif_field, Unset):
            nif_field = UNSET
        else:
            nif_field = self.nif_field

        nif_updated_at: None | str | Unset
        if isinstance(self.nif_updated_at, Unset):
            nif_updated_at = UNSET
        elif isinstance(self.nif_updated_at, datetime.datetime):
            nif_updated_at = self.nif_updated_at.isoformat()
        else:
            nif_updated_at = self.nif_updated_at

        normalized_impact_factor: float | None | Unset
        if isinstance(self.normalized_impact_factor, Unset):
            normalized_impact_factor = UNSET
        else:
            normalized_impact_factor = self.normalized_impact_factor

        source_id: None | str | Unset
        if isinstance(self.source_id, Unset):
            source_id = UNSET
        else:
            source_id = self.source_id

        two_yr_mean_citedness: float | None | Unset
        if isinstance(self.two_yr_mean_citedness, Unset):
            two_yr_mean_citedness = UNSET
        else:
            two_yr_mean_citedness = self.two_yr_mean_citedness

        works_count: int | None | Unset
        if isinstance(self.works_count, Unset):
            works_count = UNSET
        else:
            works_count = self.works_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "issn_l": issn_l,
            }
        )
        if apc_currency is not UNSET:
            field_dict["apc_currency"] = apc_currency
        if apc_source is not UNSET:
            field_dict["apc_source"] = apc_source
        if apc_usd is not UNSET:
            field_dict["apc_usd"] = apc_usd
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if h_index is not UNSET:
            field_dict["h_index"] = h_index
        if if_metric_kind is not UNSET:
            field_dict["if_metric_kind"] = if_metric_kind
        if is_in_doaj is not UNSET:
            field_dict["is_in_doaj"] = is_in_doaj
        if nif_bayes is not UNSET:
            field_dict["nif_bayes"] = nif_bayes
        if nif_ci_high is not UNSET:
            field_dict["nif_ci_high"] = nif_ci_high
        if nif_ci_low is not UNSET:
            field_dict["nif_ci_low"] = nif_ci_low
        if nif_field is not UNSET:
            field_dict["nif_field"] = nif_field
        if nif_updated_at is not UNSET:
            field_dict["nif_updated_at"] = nif_updated_at
        if normalized_impact_factor is not UNSET:
            field_dict["normalized_impact_factor"] = normalized_impact_factor
        if source_id is not UNSET:
            field_dict["source_id"] = source_id
        if two_yr_mean_citedness is not UNSET:
            field_dict["two_yr_mean_citedness"] = two_yr_mean_citedness
        if works_count is not UNSET:
            field_dict["works_count"] = works_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        issn_l = d.pop("issn_l")

        def _parse_apc_currency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        apc_currency = _parse_apc_currency(d.pop("apc_currency", UNSET))

        def _parse_apc_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        apc_source = _parse_apc_source(d.pop("apc_source", UNSET))

        def _parse_apc_usd(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        apc_usd = _parse_apc_usd(d.pop("apc_usd", UNSET))

        def _parse_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_h_index(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        h_index = _parse_h_index(d.pop("h_index", UNSET))

        def _parse_if_metric_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        if_metric_kind = _parse_if_metric_kind(d.pop("if_metric_kind", UNSET))

        def _parse_is_in_doaj(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_in_doaj = _parse_is_in_doaj(d.pop("is_in_doaj", UNSET))

        def _parse_nif_bayes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        nif_bayes = _parse_nif_bayes(d.pop("nif_bayes", UNSET))

        def _parse_nif_ci_high(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        nif_ci_high = _parse_nif_ci_high(d.pop("nif_ci_high", UNSET))

        def _parse_nif_ci_low(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        nif_ci_low = _parse_nif_ci_low(d.pop("nif_ci_low", UNSET))

        def _parse_nif_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        nif_field = _parse_nif_field(d.pop("nif_field", UNSET))

        def _parse_nif_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                nif_updated_at_type_0 = datetime.datetime.fromisoformat(data)

                return nif_updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        nif_updated_at = _parse_nif_updated_at(d.pop("nif_updated_at", UNSET))

        def _parse_normalized_impact_factor(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        normalized_impact_factor = _parse_normalized_impact_factor(d.pop("normalized_impact_factor", UNSET))

        def _parse_source_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_id = _parse_source_id(d.pop("source_id", UNSET))

        def _parse_two_yr_mean_citedness(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        two_yr_mean_citedness = _parse_two_yr_mean_citedness(d.pop("two_yr_mean_citedness", UNSET))

        def _parse_works_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        works_count = _parse_works_count(d.pop("works_count", UNSET))

        journal_metric_response = cls(
            issn_l=issn_l,
            apc_currency=apc_currency,
            apc_source=apc_source,
            apc_usd=apc_usd,
            display_name=display_name,
            h_index=h_index,
            if_metric_kind=if_metric_kind,
            is_in_doaj=is_in_doaj,
            nif_bayes=nif_bayes,
            nif_ci_high=nif_ci_high,
            nif_ci_low=nif_ci_low,
            nif_field=nif_field,
            nif_updated_at=nif_updated_at,
            normalized_impact_factor=normalized_impact_factor,
            source_id=source_id,
            two_yr_mean_citedness=two_yr_mean_citedness,
            works_count=works_count,
        )

        journal_metric_response.additional_properties = d
        return journal_metric_response

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
