from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="JournalOAShare")


@_attrs_define
class JournalOAShare:
    """
    Attributes:
        in_doaj (int):
        pct (float):
        total (int):
    """

    in_doaj: int
    pct: float
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        in_doaj = self.in_doaj

        pct = self.pct

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "in_doaj": in_doaj,
                "pct": pct,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        in_doaj = d.pop("in_doaj")

        pct = d.pop("pct")

        total = d.pop("total")

        journal_oa_share = cls(
            in_doaj=in_doaj,
            pct=pct,
            total=total,
        )

        journal_oa_share.additional_properties = d
        return journal_oa_share

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
