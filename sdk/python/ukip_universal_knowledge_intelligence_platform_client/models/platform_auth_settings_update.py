from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatformAuthSettingsUpdate")


@_attrs_define
class PlatformAuthSettingsUpdate:
    """
    Attributes:
        sso_allowed_domains (None | str | Unset):
        sso_auto_provision (bool | None | Unset):
        sso_default_role (None | str | Unset):
        sso_enabled (bool | None | Unset):
        sso_login_button_visible (bool | None | Unset):
        sso_provider_label (None | str | Unset):
    """

    sso_allowed_domains: None | str | Unset = UNSET
    sso_auto_provision: bool | None | Unset = UNSET
    sso_default_role: None | str | Unset = UNSET
    sso_enabled: bool | None | Unset = UNSET
    sso_login_button_visible: bool | None | Unset = UNSET
    sso_provider_label: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sso_allowed_domains: None | str | Unset
        if isinstance(self.sso_allowed_domains, Unset):
            sso_allowed_domains = UNSET
        else:
            sso_allowed_domains = self.sso_allowed_domains

        sso_auto_provision: bool | None | Unset
        if isinstance(self.sso_auto_provision, Unset):
            sso_auto_provision = UNSET
        else:
            sso_auto_provision = self.sso_auto_provision

        sso_default_role: None | str | Unset
        if isinstance(self.sso_default_role, Unset):
            sso_default_role = UNSET
        else:
            sso_default_role = self.sso_default_role

        sso_enabled: bool | None | Unset
        if isinstance(self.sso_enabled, Unset):
            sso_enabled = UNSET
        else:
            sso_enabled = self.sso_enabled

        sso_login_button_visible: bool | None | Unset
        if isinstance(self.sso_login_button_visible, Unset):
            sso_login_button_visible = UNSET
        else:
            sso_login_button_visible = self.sso_login_button_visible

        sso_provider_label: None | str | Unset
        if isinstance(self.sso_provider_label, Unset):
            sso_provider_label = UNSET
        else:
            sso_provider_label = self.sso_provider_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sso_allowed_domains is not UNSET:
            field_dict["sso_allowed_domains"] = sso_allowed_domains
        if sso_auto_provision is not UNSET:
            field_dict["sso_auto_provision"] = sso_auto_provision
        if sso_default_role is not UNSET:
            field_dict["sso_default_role"] = sso_default_role
        if sso_enabled is not UNSET:
            field_dict["sso_enabled"] = sso_enabled
        if sso_login_button_visible is not UNSET:
            field_dict["sso_login_button_visible"] = sso_login_button_visible
        if sso_provider_label is not UNSET:
            field_dict["sso_provider_label"] = sso_provider_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_sso_allowed_domains(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sso_allowed_domains = _parse_sso_allowed_domains(d.pop("sso_allowed_domains", UNSET))

        def _parse_sso_auto_provision(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        sso_auto_provision = _parse_sso_auto_provision(d.pop("sso_auto_provision", UNSET))

        def _parse_sso_default_role(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sso_default_role = _parse_sso_default_role(d.pop("sso_default_role", UNSET))

        def _parse_sso_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        sso_enabled = _parse_sso_enabled(d.pop("sso_enabled", UNSET))

        def _parse_sso_login_button_visible(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        sso_login_button_visible = _parse_sso_login_button_visible(d.pop("sso_login_button_visible", UNSET))

        def _parse_sso_provider_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sso_provider_label = _parse_sso_provider_label(d.pop("sso_provider_label", UNSET))

        platform_auth_settings_update = cls(
            sso_allowed_domains=sso_allowed_domains,
            sso_auto_provision=sso_auto_provision,
            sso_default_role=sso_default_role,
            sso_enabled=sso_enabled,
            sso_login_button_visible=sso_login_button_visible,
            sso_provider_label=sso_provider_label,
        )

        platform_auth_settings_update.additional_properties = d
        return platform_auth_settings_update

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
