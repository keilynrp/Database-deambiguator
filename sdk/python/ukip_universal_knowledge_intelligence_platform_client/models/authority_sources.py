from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthoritySources")


@_attrs_define
class AuthoritySources:
    """
    Attributes:
        bibliographic (list[str] | Unset):
        identity (list[str] | Unset):
        institutional (list[str] | Unset):
    """

    bibliographic: list[str] | Unset = UNSET
    identity: list[str] | Unset = UNSET
    institutional: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bibliographic: list[str] | Unset = UNSET
        if not isinstance(self.bibliographic, Unset):
            bibliographic = self.bibliographic

        identity: list[str] | Unset = UNSET
        if not isinstance(self.identity, Unset):
            identity = self.identity

        institutional: list[str] | Unset = UNSET
        if not isinstance(self.institutional, Unset):
            institutional = self.institutional

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bibliographic is not UNSET:
            field_dict["bibliographic"] = bibliographic
        if identity is not UNSET:
            field_dict["identity"] = identity
        if institutional is not UNSET:
            field_dict["institutional"] = institutional

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bibliographic = cast(list[str], d.pop("bibliographic", UNSET))

        identity = cast(list[str], d.pop("identity", UNSET))

        institutional = cast(list[str], d.pop("institutional", UNSET))

        authority_sources = cls(
            bibliographic=bibliographic,
            identity=identity,
            institutional=institutional,
        )

        authority_sources.additional_properties = d
        return authority_sources

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
