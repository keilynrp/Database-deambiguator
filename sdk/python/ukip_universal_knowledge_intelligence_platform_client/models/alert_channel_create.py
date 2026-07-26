from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AlertChannelCreate")


@_attrs_define
class AlertChannelCreate:
    """
    Attributes:
        name (str):
        webhook_url (str):
        events (list[str] | Unset):
        type_ (str | Unset):  Default: 'slack'.
    """

    name: str
    webhook_url: str
    events: list[str] | Unset = UNSET
    type_: str | Unset = "slack"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        webhook_url = self.webhook_url

        events: list[str] | Unset = UNSET
        if not isinstance(self.events, Unset):
            events = self.events

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "webhook_url": webhook_url,
            }
        )
        if events is not UNSET:
            field_dict["events"] = events
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        webhook_url = d.pop("webhook_url")

        events = cast(list[str], d.pop("events", UNSET))

        type_ = d.pop("type", UNSET)

        alert_channel_create = cls(
            name=name,
            webhook_url=webhook_url,
            events=events,
            type_=type_,
        )

        alert_channel_create.additional_properties = d
        return alert_channel_create

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
