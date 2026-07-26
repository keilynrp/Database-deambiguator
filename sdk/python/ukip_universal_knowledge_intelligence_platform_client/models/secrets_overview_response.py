from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.secret_rotation_event_response import SecretRotationEventResponse
    from ..models.secrets_check_response import SecretsCheckResponse


T = TypeVar("T", bound="SecretsOverviewResponse")


@_attrs_define
class SecretsOverviewResponse:
    """
    Attributes:
        check (SecretsCheckResponse):
        events (list[SecretRotationEventResponse]):
    """

    check: SecretsCheckResponse
    events: list[SecretRotationEventResponse]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        check = self.check.to_dict()

        events = []
        for events_item_data in self.events:
            events_item = events_item_data.to_dict()
            events.append(events_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "check": check,
                "events": events,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secret_rotation_event_response import SecretRotationEventResponse
        from ..models.secrets_check_response import SecretsCheckResponse

        d = dict(src_dict)
        check = SecretsCheckResponse.from_dict(d.pop("check"))

        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = SecretRotationEventResponse.from_dict(events_item_data)

            events.append(events_item)

        secrets_overview_response = cls(
            check=check,
            events=events,
        )

        secrets_overview_response.additional_properties = d
        return secrets_overview_response

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
