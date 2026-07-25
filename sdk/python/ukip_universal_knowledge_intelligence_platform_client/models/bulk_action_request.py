from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkActionRequest")


@_attrs_define
class BulkActionRequest:
    """
    Attributes:
        ids (list[int]):
        also_create_rules (bool | Unset):  Default: True.
    """

    ids: list[int]
    also_create_rules: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ids = self.ids

        also_create_rules = self.also_create_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ids": ids,
            }
        )
        if also_create_rules is not UNSET:
            field_dict["also_create_rules"] = also_create_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ids = cast(list[int], d.pop("ids"))

        also_create_rules = d.pop("also_create_rules", UNSET)

        bulk_action_request = cls(
            ids=ids,
            also_create_rules=also_create_rules,
        )

        bulk_action_request.additional_properties = d
        return bulk_action_request

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
