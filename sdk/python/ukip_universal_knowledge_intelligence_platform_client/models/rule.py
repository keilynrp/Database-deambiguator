from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Rule")


@_attrs_define
class Rule:
    """
    Attributes:
        field_name (str):
        id (int):
        normalized_value (str):
        original_value (str):
        is_regex (bool | Unset):  Default: False.
    """

    field_name: str
    id: int
    normalized_value: str
    original_value: str
    is_regex: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_name = self.field_name

        id = self.id

        normalized_value = self.normalized_value

        original_value = self.original_value

        is_regex = self.is_regex

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field_name": field_name,
                "id": id,
                "normalized_value": normalized_value,
                "original_value": original_value,
            }
        )
        if is_regex is not UNSET:
            field_dict["is_regex"] = is_regex

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_name = d.pop("field_name")

        id = d.pop("id")

        normalized_value = d.pop("normalized_value")

        original_value = d.pop("original_value")

        is_regex = d.pop("is_regex", UNSET)

        rule = cls(
            field_name=field_name,
            id=id,
            normalized_value=normalized_value,
            original_value=original_value,
            is_regex=is_regex,
        )

        rule.additional_properties = d
        return rule

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
