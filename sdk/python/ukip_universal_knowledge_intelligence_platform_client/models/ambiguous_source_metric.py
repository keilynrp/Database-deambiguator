from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AmbiguousSourceMetric")


@_attrs_define
class AmbiguousSourceMetric:
    """
    Attributes:
        pending_suggestions (int):
        source_schema (str):
    """

    pending_suggestions: int
    source_schema: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pending_suggestions = self.pending_suggestions

        source_schema = self.source_schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "pending_suggestions": pending_suggestions,
                "source_schema": source_schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        pending_suggestions = d.pop("pending_suggestions")

        source_schema = d.pop("source_schema")

        ambiguous_source_metric = cls(
            pending_suggestions=pending_suggestions,
            source_schema=source_schema,
        )

        ambiguous_source_metric.additional_properties = d
        return ambiguous_source_metric

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
