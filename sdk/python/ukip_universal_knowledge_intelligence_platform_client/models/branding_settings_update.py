from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BrandingSettingsUpdate")


@_attrs_define
class BrandingSettingsUpdate:
    """
    Attributes:
        accent_color (None | str | Unset):
        favicon_url (None | str | Unset):
        footer_text (None | str | Unset):
        logo_url (None | str | Unset):
        platform_name (None | str | Unset):
    """

    accent_color: None | str | Unset = UNSET
    favicon_url: None | str | Unset = UNSET
    footer_text: None | str | Unset = UNSET
    logo_url: None | str | Unset = UNSET
    platform_name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        accent_color: None | str | Unset
        if isinstance(self.accent_color, Unset):
            accent_color = UNSET
        else:
            accent_color = self.accent_color

        favicon_url: None | str | Unset
        if isinstance(self.favicon_url, Unset):
            favicon_url = UNSET
        else:
            favicon_url = self.favicon_url

        footer_text: None | str | Unset
        if isinstance(self.footer_text, Unset):
            footer_text = UNSET
        else:
            footer_text = self.footer_text

        logo_url: None | str | Unset
        if isinstance(self.logo_url, Unset):
            logo_url = UNSET
        else:
            logo_url = self.logo_url

        platform_name: None | str | Unset
        if isinstance(self.platform_name, Unset):
            platform_name = UNSET
        else:
            platform_name = self.platform_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if accent_color is not UNSET:
            field_dict["accent_color"] = accent_color
        if favicon_url is not UNSET:
            field_dict["favicon_url"] = favicon_url
        if footer_text is not UNSET:
            field_dict["footer_text"] = footer_text
        if logo_url is not UNSET:
            field_dict["logo_url"] = logo_url
        if platform_name is not UNSET:
            field_dict["platform_name"] = platform_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_accent_color(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        accent_color = _parse_accent_color(d.pop("accent_color", UNSET))

        def _parse_favicon_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        favicon_url = _parse_favicon_url(d.pop("favicon_url", UNSET))

        def _parse_footer_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        footer_text = _parse_footer_text(d.pop("footer_text", UNSET))

        def _parse_logo_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        logo_url = _parse_logo_url(d.pop("logo_url", UNSET))

        def _parse_platform_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        platform_name = _parse_platform_name(d.pop("platform_name", UNSET))

        branding_settings_update = cls(
            accent_color=accent_color,
            favicon_url=favicon_url,
            footer_text=footer_text,
            logo_url=logo_url,
            platform_name=platform_name,
        )

        branding_settings_update.additional_properties = d
        return branding_settings_update

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
