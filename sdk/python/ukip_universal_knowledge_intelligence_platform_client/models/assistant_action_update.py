from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssistantActionUpdate")


@_attrs_define
class AssistantActionUpdate:
    """
    Attributes:
        allowed_roles (list[str] | None | Unset):
        enabled (bool | None | Unset):
        requires_confirmation (bool | None | Unset):
    """

    allowed_roles: list[str] | None | Unset = UNSET
    enabled: bool | None | Unset = UNSET
    requires_confirmation: bool | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_roles: list[str] | None | Unset
        if isinstance(self.allowed_roles, Unset):
            allowed_roles = UNSET
        elif isinstance(self.allowed_roles, list):
            allowed_roles = self.allowed_roles

        else:
            allowed_roles = self.allowed_roles

        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        requires_confirmation: bool | None | Unset
        if isinstance(self.requires_confirmation, Unset):
            requires_confirmation = UNSET
        else:
            requires_confirmation = self.requires_confirmation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allowed_roles is not UNSET:
            field_dict["allowed_roles"] = allowed_roles
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if requires_confirmation is not UNSET:
            field_dict["requires_confirmation"] = requires_confirmation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_allowed_roles(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_roles_type_0 = cast(list[str], data)

                return allowed_roles_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        allowed_roles = _parse_allowed_roles(d.pop("allowed_roles", UNSET))

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_requires_confirmation(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        requires_confirmation = _parse_requires_confirmation(d.pop("requires_confirmation", UNSET))

        assistant_action_update = cls(
            allowed_roles=allowed_roles,
            enabled=enabled,
            requires_confirmation=requires_confirmation,
        )

        assistant_action_update.additional_properties = d
        return assistant_action_update

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
