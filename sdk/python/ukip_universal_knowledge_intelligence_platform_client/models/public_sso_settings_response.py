from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PublicSsoSettingsResponse")


@_attrs_define
class PublicSsoSettingsResponse:
    """
    Attributes:
        sso_enabled (bool):
        sso_login_button_visible (bool):
        sso_provider_configured (bool):
        sso_provider_label (str):
    """

    sso_enabled: bool
    sso_login_button_visible: bool
    sso_provider_configured: bool
    sso_provider_label: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sso_enabled = self.sso_enabled

        sso_login_button_visible = self.sso_login_button_visible

        sso_provider_configured = self.sso_provider_configured

        sso_provider_label = self.sso_provider_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sso_enabled": sso_enabled,
                "sso_login_button_visible": sso_login_button_visible,
                "sso_provider_configured": sso_provider_configured,
                "sso_provider_label": sso_provider_label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sso_enabled = d.pop("sso_enabled")

        sso_login_button_visible = d.pop("sso_login_button_visible")

        sso_provider_configured = d.pop("sso_provider_configured")

        sso_provider_label = d.pop("sso_provider_label")

        public_sso_settings_response = cls(
            sso_enabled=sso_enabled,
            sso_login_button_visible=sso_login_button_visible,
            sso_provider_configured=sso_provider_configured,
            sso_provider_label=sso_provider_label,
        )

        public_sso_settings_response.additional_properties = d
        return public_sso_settings_response

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
