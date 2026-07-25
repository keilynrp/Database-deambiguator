from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FieldCorrespondenceRollbackResponse")


@_attrs_define
class FieldCorrespondenceRollbackResponse:
    """
    Attributes:
        job_id (int):
        records_restored (int):
        reverted (bool):
    """

    job_id: int
    records_restored: int
    reverted: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        records_restored = self.records_restored

        reverted = self.reverted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "records_restored": records_restored,
                "reverted": reverted,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id")

        records_restored = d.pop("records_restored")

        reverted = d.pop("reverted")

        field_correspondence_rollback_response = cls(
            job_id=job_id,
            records_restored=records_restored,
            reverted=reverted,
        )

        field_correspondence_rollback_response.additional_properties = d
        return field_correspondence_rollback_response

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
