from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthorityConfirmRequest")


@_attrs_define
class AuthorityConfirmRequest:
    """
    Attributes:
        also_create_rule (bool | Unset):  Default: True.
    """

    also_create_rule: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        also_create_rule = self.also_create_rule

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if also_create_rule is not UNSET:
            field_dict["also_create_rule"] = also_create_rule

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        also_create_rule = d.pop("also_create_rule", UNSET)

        authority_confirm_request = cls(
            also_create_rule=also_create_rule,
        )

        authority_confirm_request.additional_properties = d
        return authority_confirm_request

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
