from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ScheduledImportCreate")


@_attrs_define
class ScheduledImportCreate:
    """
    Attributes:
        interval_minutes (int):
        name (str):
        store_id (int):
    """

    interval_minutes: int
    name: str
    store_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        interval_minutes = self.interval_minutes

        name = self.name

        store_id = self.store_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "interval_minutes": interval_minutes,
                "name": name,
                "store_id": store_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        interval_minutes = d.pop("interval_minutes")

        name = d.pop("name")

        store_id = d.pop("store_id")

        scheduled_import_create = cls(
            interval_minutes=interval_minutes,
            name=name,
            store_id=store_id,
        )

        scheduled_import_create.additional_properties = d
        return scheduled_import_create

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
