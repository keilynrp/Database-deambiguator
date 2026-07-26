from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.store_connection_create_platform import StoreConnectionCreatePlatform
from ..models.store_connection_create_sync_direction import StoreConnectionCreateSyncDirection
from ..types import UNSET, Unset

T = TypeVar("T", bound="StoreConnectionCreate")


@_attrs_define
class StoreConnectionCreate:
    """
    Attributes:
        base_url (str):
        name (str):
        platform (StoreConnectionCreatePlatform):
        access_token (None | str | Unset):
        api_key (None | str | Unset):
        api_secret (None | str | Unset):
        custom_headers (None | str | Unset):
        notes (None | str | Unset):
        sync_direction (StoreConnectionCreateSyncDirection | Unset):  Default:
            StoreConnectionCreateSyncDirection.BIDIRECTIONAL.
    """

    base_url: str
    name: str
    platform: StoreConnectionCreatePlatform
    access_token: None | str | Unset = UNSET
    api_key: None | str | Unset = UNSET
    api_secret: None | str | Unset = UNSET
    custom_headers: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    sync_direction: StoreConnectionCreateSyncDirection | Unset = StoreConnectionCreateSyncDirection.BIDIRECTIONAL
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_url = self.base_url

        name = self.name

        platform = self.platform.value

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

        custom_headers: None | str | Unset
        if isinstance(self.custom_headers, Unset):
            custom_headers = UNSET
        else:
            custom_headers = self.custom_headers

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        sync_direction: str | Unset = UNSET
        if not isinstance(self.sync_direction, Unset):
            sync_direction = self.sync_direction.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_url": base_url,
                "name": name,
                "platform": platform,
            }
        )
        if access_token is not UNSET:
            field_dict["access_token"] = access_token
        if api_key is not UNSET:
            field_dict["api_key"] = api_key
        if api_secret is not UNSET:
            field_dict["api_secret"] = api_secret
        if custom_headers is not UNSET:
            field_dict["custom_headers"] = custom_headers
        if notes is not UNSET:
            field_dict["notes"] = notes
        if sync_direction is not UNSET:
            field_dict["sync_direction"] = sync_direction

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        base_url = d.pop("base_url")

        name = d.pop("name")

        platform = StoreConnectionCreatePlatform(d.pop("platform"))

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

        def _parse_custom_headers(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        custom_headers = _parse_custom_headers(d.pop("custom_headers", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        _sync_direction = d.pop("sync_direction", UNSET)
        sync_direction: StoreConnectionCreateSyncDirection | Unset
        if isinstance(_sync_direction, Unset):
            sync_direction = UNSET
        else:
            sync_direction = StoreConnectionCreateSyncDirection(_sync_direction)

        store_connection_create = cls(
            base_url=base_url,
            name=name,
            platform=platform,
            access_token=access_token,
            api_key=api_key,
            api_secret=api_secret,
            custom_headers=custom_headers,
            notes=notes,
            sync_direction=sync_direction,
        )

        store_connection_create.additional_properties = d
        return store_connection_create

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
