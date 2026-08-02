from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImportStatusResponse")


@_attrs_define
class ImportStatusResponse:
    """
    Attributes:
        job_id (str):
        status (str):
        error (None | str | Unset):
        progress (float | Unset):  Default: 0.0.
        query_translation (None | str | Unset):
        records_inserted (int | Unset):  Default: 0.
        total (int | Unset):  Default: 0.
        warning (None | str | Unset):
    """

    job_id: str
    status: str
    error: None | str | Unset = UNSET
    progress: float | Unset = 0.0
    query_translation: None | str | Unset = UNSET
    records_inserted: int | Unset = 0
    total: int | Unset = 0
    warning: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        status = self.status

        error: None | str | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        else:
            error = self.error

        progress = self.progress

        query_translation: None | str | Unset
        if isinstance(self.query_translation, Unset):
            query_translation = UNSET
        else:
            query_translation = self.query_translation

        records_inserted = self.records_inserted

        total = self.total

        warning: None | str | Unset
        if isinstance(self.warning, Unset):
            warning = UNSET
        else:
            warning = self.warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "status": status,
            }
        )
        if error is not UNSET:
            field_dict["error"] = error
        if progress is not UNSET:
            field_dict["progress"] = progress
        if query_translation is not UNSET:
            field_dict["query_translation"] = query_translation
        if records_inserted is not UNSET:
            field_dict["records_inserted"] = records_inserted
        if total is not UNSET:
            field_dict["total"] = total
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id")

        status = d.pop("status")

        def _parse_error(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        progress = d.pop("progress", UNSET)

        def _parse_query_translation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        query_translation = _parse_query_translation(d.pop("query_translation", UNSET))

        records_inserted = d.pop("records_inserted", UNSET)

        total = d.pop("total", UNSET)

        def _parse_warning(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        warning = _parse_warning(d.pop("warning", UNSET))

        import_status_response = cls(
            job_id=job_id,
            status=status,
            error=error,
            progress=progress,
            query_translation=query_translation,
            records_inserted=records_inserted,
            total=total,
            warning=warning,
        )

        import_status_response.additional_properties = d
        return import_status_response

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
