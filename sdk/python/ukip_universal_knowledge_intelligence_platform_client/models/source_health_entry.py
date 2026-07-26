from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SourceHealthEntry")


@_attrs_define
class SourceHealthEntry:
    """Circuit-breaker state for a single enrichment source.

    Attributes:
        failure_count (int):
        source (str):
        state (str):
        success_count (int):
        last_failure (float | None | Unset):
        last_used (float | None | Unset):
    """

    failure_count: int
    source: str
    state: str
    success_count: int
    last_failure: float | None | Unset = UNSET
    last_used: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        failure_count = self.failure_count

        source = self.source

        state = self.state

        success_count = self.success_count

        last_failure: float | None | Unset
        if isinstance(self.last_failure, Unset):
            last_failure = UNSET
        else:
            last_failure = self.last_failure

        last_used: float | None | Unset
        if isinstance(self.last_used, Unset):
            last_used = UNSET
        else:
            last_used = self.last_used

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "failure_count": failure_count,
                "source": source,
                "state": state,
                "success_count": success_count,
            }
        )
        if last_failure is not UNSET:
            field_dict["last_failure"] = last_failure
        if last_used is not UNSET:
            field_dict["last_used"] = last_used

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        failure_count = d.pop("failure_count")

        source = d.pop("source")

        state = d.pop("state")

        success_count = d.pop("success_count")

        def _parse_last_failure(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        last_failure = _parse_last_failure(d.pop("last_failure", UNSET))

        def _parse_last_used(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        last_used = _parse_last_used(d.pop("last_used", UNSET))

        source_health_entry = cls(
            failure_count=failure_count,
            source=source,
            state=state,
            success_count=success_count,
            last_failure=last_failure,
            last_used=last_used,
        )

        source_health_entry.additional_properties = d
        return source_health_entry

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
