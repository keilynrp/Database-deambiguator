from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NotificationSettingsUpdate")


@_attrs_define
class NotificationSettingsUpdate:
    """
    Attributes:
        enabled (bool | None | Unset):
        from_email (None | str | Unset):
        notify_on_authority_confirm (bool | None | Unset):
        notify_on_enrichment_batch (bool | None | Unset):
        recipient_email (None | str | Unset):
        smtp_host (None | str | Unset):
        smtp_password (None | str | Unset):
        smtp_port (int | None | Unset):
        smtp_user (None | str | Unset):
    """

    enabled: bool | None | Unset = UNSET
    from_email: None | str | Unset = UNSET
    notify_on_authority_confirm: bool | None | Unset = UNSET
    notify_on_enrichment_batch: bool | None | Unset = UNSET
    recipient_email: None | str | Unset = UNSET
    smtp_host: None | str | Unset = UNSET
    smtp_password: None | str | Unset = UNSET
    smtp_port: int | None | Unset = UNSET
    smtp_user: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled: bool | None | Unset
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        from_email: None | str | Unset
        if isinstance(self.from_email, Unset):
            from_email = UNSET
        else:
            from_email = self.from_email

        notify_on_authority_confirm: bool | None | Unset
        if isinstance(self.notify_on_authority_confirm, Unset):
            notify_on_authority_confirm = UNSET
        else:
            notify_on_authority_confirm = self.notify_on_authority_confirm

        notify_on_enrichment_batch: bool | None | Unset
        if isinstance(self.notify_on_enrichment_batch, Unset):
            notify_on_enrichment_batch = UNSET
        else:
            notify_on_enrichment_batch = self.notify_on_enrichment_batch

        recipient_email: None | str | Unset
        if isinstance(self.recipient_email, Unset):
            recipient_email = UNSET
        else:
            recipient_email = self.recipient_email

        smtp_host: None | str | Unset
        if isinstance(self.smtp_host, Unset):
            smtp_host = UNSET
        else:
            smtp_host = self.smtp_host

        smtp_password: None | str | Unset
        if isinstance(self.smtp_password, Unset):
            smtp_password = UNSET
        else:
            smtp_password = self.smtp_password

        smtp_port: int | None | Unset
        if isinstance(self.smtp_port, Unset):
            smtp_port = UNSET
        else:
            smtp_port = self.smtp_port

        smtp_user: None | str | Unset
        if isinstance(self.smtp_user, Unset):
            smtp_user = UNSET
        else:
            smtp_user = self.smtp_user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if from_email is not UNSET:
            field_dict["from_email"] = from_email
        if notify_on_authority_confirm is not UNSET:
            field_dict["notify_on_authority_confirm"] = notify_on_authority_confirm
        if notify_on_enrichment_batch is not UNSET:
            field_dict["notify_on_enrichment_batch"] = notify_on_enrichment_batch
        if recipient_email is not UNSET:
            field_dict["recipient_email"] = recipient_email
        if smtp_host is not UNSET:
            field_dict["smtp_host"] = smtp_host
        if smtp_password is not UNSET:
            field_dict["smtp_password"] = smtp_password
        if smtp_port is not UNSET:
            field_dict["smtp_port"] = smtp_port
        if smtp_user is not UNSET:
            field_dict["smtp_user"] = smtp_user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_enabled(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_from_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        from_email = _parse_from_email(d.pop("from_email", UNSET))

        def _parse_notify_on_authority_confirm(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        notify_on_authority_confirm = _parse_notify_on_authority_confirm(d.pop("notify_on_authority_confirm", UNSET))

        def _parse_notify_on_enrichment_batch(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        notify_on_enrichment_batch = _parse_notify_on_enrichment_batch(d.pop("notify_on_enrichment_batch", UNSET))

        def _parse_recipient_email(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        recipient_email = _parse_recipient_email(d.pop("recipient_email", UNSET))

        def _parse_smtp_host(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        smtp_host = _parse_smtp_host(d.pop("smtp_host", UNSET))

        def _parse_smtp_password(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        smtp_password = _parse_smtp_password(d.pop("smtp_password", UNSET))

        def _parse_smtp_port(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        smtp_port = _parse_smtp_port(d.pop("smtp_port", UNSET))

        def _parse_smtp_user(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        smtp_user = _parse_smtp_user(d.pop("smtp_user", UNSET))

        notification_settings_update = cls(
            enabled=enabled,
            from_email=from_email,
            notify_on_authority_confirm=notify_on_authority_confirm,
            notify_on_enrichment_batch=notify_on_enrichment_batch,
            recipient_email=recipient_email,
            smtp_host=smtp_host,
            smtp_password=smtp_password,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
        )

        notification_settings_update.additional_properties = d
        return notification_settings_update

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
