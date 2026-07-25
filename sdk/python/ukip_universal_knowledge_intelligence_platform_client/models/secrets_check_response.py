from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.secrets_check_response_status import SecretsCheckResponseStatus

if TYPE_CHECKING:
    from ..models.secrets_check_response_details import SecretsCheckResponseDetails


T = TypeVar("T", bound="SecretsCheckResponse")


@_attrs_define
class SecretsCheckResponse:
    """
    Attributes:
        details (SecretsCheckResponseDetails):
        id (str):
        status (SecretsCheckResponseStatus):
        summary (str):
    """

    details: SecretsCheckResponseDetails
    id: str
    status: SecretsCheckResponseStatus
    summary: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        details = self.details.to_dict()

        id = self.id

        status = self.status.value

        summary = self.summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "details": details,
                "id": id,
                "status": status,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.secrets_check_response_details import SecretsCheckResponseDetails

        d = dict(src_dict)
        details = SecretsCheckResponseDetails.from_dict(d.pop("details"))

        id = d.pop("id")

        status = SecretsCheckResponseStatus(d.pop("status"))

        summary = d.pop("summary")

        secrets_check_response = cls(
            details=details,
            id=id,
            status=status,
            summary=summary,
        )

        secrets_check_response.additional_properties = d
        return secrets_check_response

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
