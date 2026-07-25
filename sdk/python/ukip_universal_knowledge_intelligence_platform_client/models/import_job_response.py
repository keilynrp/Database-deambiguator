from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImportJobResponse")


@_attrs_define
class ImportJobResponse:
    """
    Attributes:
        job_id (str):
        status (str):
        record_count (int | Unset):  Default: 0.
    """

    job_id: str
    status: str
    record_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        status = self.status

        record_count = self.record_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "status": status,
            }
        )
        if record_count is not UNSET:
            field_dict["record_count"] = record_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id")

        status = d.pop("status")

        record_count = d.pop("record_count", UNSET)

        import_job_response = cls(
            job_id=job_id,
            status=status,
            record_count=record_count,
        )

        import_job_response.additional_properties = d
        return import_job_response

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
