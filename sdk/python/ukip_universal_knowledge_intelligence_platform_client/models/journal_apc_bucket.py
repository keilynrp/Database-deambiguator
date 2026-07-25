from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalApcBucket")


@_attrs_define
class JournalApcBucket:
    """
    Attributes:
        count (int):
        currency (None | str | Unset):
        max_ (int | None | Unset):
        median (float | None | Unset):
        min_ (int | None | Unset):
    """

    count: int
    currency: None | str | Unset = UNSET
    max_: int | None | Unset = UNSET
    median: float | None | Unset = UNSET
    min_: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        currency: None | str | Unset
        if isinstance(self.currency, Unset):
            currency = UNSET
        else:
            currency = self.currency

        max_: int | None | Unset
        if isinstance(self.max_, Unset):
            max_ = UNSET
        else:
            max_ = self.max_

        median: float | None | Unset
        if isinstance(self.median, Unset):
            median = UNSET
        else:
            median = self.median

        min_: int | None | Unset
        if isinstance(self.min_, Unset):
            min_ = UNSET
        else:
            min_ = self.min_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "count": count,
            }
        )
        if currency is not UNSET:
            field_dict["currency"] = currency
        if max_ is not UNSET:
            field_dict["max"] = max_
        if median is not UNSET:
            field_dict["median"] = median
        if min_ is not UNSET:
            field_dict["min"] = min_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        count = d.pop("count")

        def _parse_currency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        currency = _parse_currency(d.pop("currency", UNSET))

        def _parse_max_(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_ = _parse_max_(d.pop("max", UNSET))

        def _parse_median(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        median = _parse_median(d.pop("median", UNSET))

        def _parse_min_(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        min_ = _parse_min_(d.pop("min", UNSET))

        journal_apc_bucket = cls(
            count=count,
            currency=currency,
            max_=max_,
            median=median,
            min_=min_,
        )

        journal_apc_bucket.additional_properties = d
        return journal_apc_bucket

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
