from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.store_connection_update_platform_type_0 import StoreConnectionUpdatePlatformType0
from ..models.store_connection_update_sync_direction_type_0 import StoreConnectionUpdateSyncDirectionType0
from ..types import UNSET, Unset

T = TypeVar("T", bound="StoreConnectionUpdate")


@_attrs_define
class StoreConnectionUpdate:
    """
    Attributes:
        access_token (None | str | Unset):
        api_key (None | str | Unset):
        api_secret (None | str | Unset):
        base_url (None | str | Unset):
        custom_headers (None | str | Unset):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        notes (None | str | Unset):
        platform (None | StoreConnectionUpdatePlatformType0 | Unset):
        sync_direction (None | StoreConnectionUpdateSyncDirectionType0 | Unset):
    """

    access_token: None | str | Unset = UNSET
    api_key: None | str | Unset = UNSET
    api_secret: None | str | Unset = UNSET
    base_url: None | str | Unset = UNSET
    custom_headers: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    platform: None | StoreConnectionUpdatePlatformType0 | Unset = UNSET
    sync_direction: None | StoreConnectionUpdateSyncDirectionType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        access_token: None | str | Unset
        if isinstance(self.access_token, Unset):
            access_token = UNSET
        else:
            access_token = self.access_token

        api_key: None | str | Unset
        if isinstance(self.api_key, Unset):
            api_key = UNSET
        else:
            api_key = self.api_key

        api_secret: None | str | Unset
        if isinstance(self.api_secret, Unset):
            api_secret = UNSET
        else:
            api_secret = self.api_secret

        base_url: None | str | Unset
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        custom_headers: None | str | Unset
        if isinstance(self.custom_headers, Unset):
            custom_headers = UNSET
        else:
            custom_headers = self.custom_headers

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        platform: None | str | Unset
        if isinstance(self.platform, Unset):
            platform = UNSET
        elif isinstance(self.platform, StoreConnectionUpdatePlatformType0):
            platform = self.platform.value
        else:
            platform = self.platform

        sync_direction: None | str | Unset
        if isinstance(self.sync_direction, Unset):
            sync_direction = UNSET
        elif isinstance(self.sync_direction, StoreConnectionUpdateSyncDirectionType0):
            sync_direction = self.sync_direction.value
        else:
            sync_direction = self.sync_direction

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if api_secret is not UNSET:
            field_dict["api_secret"] = api_secret
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if custom_headers is not UNSET:
            field_dict["custom_headers"] = custom_headers
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if platform is not UNSET:
            field_dict["platform"] = platform
        if sync_direction is not UNSET:
            field_dict["sync_direction"] = sync_direction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_access_token(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        access_token = _parse_access_token(d.pop("access_token", UNSET))

        def _parse_api_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_key = _parse_api_key(d.pop("api_key", UNSET))

        def _parse_api_secret(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_secret = _parse_api_secret(d.pop("api_secret", UNSET))

        def _parse_base_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_custom_headers(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        custom_headers = _parse_custom_headers(d.pop("custom_headers", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_platform(data: object) -> None | StoreConnectionUpdatePlatformType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                platform_type_0 = StoreConnectionUpdatePlatformType0(data)

                return platform_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StoreConnectionUpdatePlatformType0 | Unset, data)

        platform = _parse_platform(d.pop("platform", UNSET))

        def _parse_sync_direction(data: object) -> None | StoreConnectionUpdateSyncDirectionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sync_direction_type_0 = StoreConnectionUpdateSyncDirectionType0(data)

                return sync_direction_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | StoreConnectionUpdateSyncDirectionType0 | Unset, data)

        sync_direction = _parse_sync_direction(d.pop("sync_direction", UNSET))

        store_connection_update = cls(
            access_token=access_token,
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            custom_headers=custom_headers,
            is_active=is_active,
            name=name,
            notes=notes,
            platform=platform,
            sync_direction=sync_direction,
        )

        store_connection_update.additional_properties = d
        return store_connection_update

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
