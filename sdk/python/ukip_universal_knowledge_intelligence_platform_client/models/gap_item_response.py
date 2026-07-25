from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GapItemResponse")


@_attrs_define
class GapItemResponse:
    """
    Attributes:
        action (str):
        affected_count (int):
        category (str):
        description (str):
        pct (float):
        severity (str):
        title (str):
        total_count (int):
    """

    action: str
    affected_count: int
    category: str
    description: str
    pct: float
    severity: str
    title: str
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action

        affected_count = self.affected_count

        category = self.category

        description = self.description

        pct = self.pct

        severity = self.severity

        title = self.title

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "affected_count": affected_count,
                "category": category,
                "description": description,
                "pct": pct,
                "severity": severity,
                "title": title,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = d.pop("action")

        affected_count = d.pop("affected_count")

        category = d.pop("category")

        description = d.pop("description")

        pct = d.pop("pct")

        severity = d.pop("severity")

        title = d.pop("title")

        total_count = d.pop("total_count")

        gap_item_response = cls(
            action=action,
            affected_count=affected_count,
            category=category,
            description=description,
            pct=pct,
            severity=severity,
            title=title,
            total_count=total_count,
        )

        gap_item_response.additional_properties = d
        return gap_item_response

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
