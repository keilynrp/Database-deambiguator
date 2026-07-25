from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ImportBatchResponse")


@_attrs_define
class ImportBatchResponse:
    """
    Attributes:
        domain_id (str):
        id (int):
        source_type (str):
        created_at (datetime.datetime | None | Unset):
        created_by (int | None | Unset):
        entity_type_hint (None | str | Unset):
        file_format (None | str | Unset):
        file_name (None | str | Unset):
        org_id (int | None | Unset):
        source_label (None | str | Unset):
        total_rows (int | Unset):  Default: 0.
    """

    domain_id: str
    id: int
    source_type: str
    created_at: datetime.datetime | None | Unset = UNSET
    created_by: int | None | Unset = UNSET
    entity_type_hint: None | str | Unset = UNSET
    file_format: None | str | Unset = UNSET
    file_name: None | str | Unset = UNSET
    org_id: int | None | Unset = UNSET
    source_label: None | str | Unset = UNSET
    total_rows: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        id = self.id

        source_type = self.source_type

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        created_by: int | None | Unset
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        entity_type_hint: None | str | Unset
        if isinstance(self.entity_type_hint, Unset):
            entity_type_hint = UNSET
        else:
            entity_type_hint = self.entity_type_hint

        file_format: None | str | Unset
        if isinstance(self.file_format, Unset):
            file_format = UNSET
        else:
            file_format = self.file_format

        file_name: None | str | Unset
        if isinstance(self.file_name, Unset):
            file_name = UNSET
        else:
            file_name = self.file_name

        org_id: int | None | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        source_label: None | str | Unset
        if isinstance(self.source_label, Unset):
            source_label = UNSET
        else:
            source_label = self.source_label

        total_rows = self.total_rows

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "id": id,
                "source_type": source_type,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if entity_type_hint is not UNSET:
            field_dict["entity_type_hint"] = entity_type_hint
        if file_format is not UNSET:
            field_dict["file_format"] = file_format
        if file_name is not UNSET:
            field_dict["file_name"] = file_name
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if source_label is not UNSET:
            field_dict["source_label"] = source_label
        if total_rows is not UNSET:
            field_dict["total_rows"] = total_rows

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        id = d.pop("id")

        source_type = d.pop("source_type")

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = datetime.datetime.fromisoformat(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_created_by(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        created_by = _parse_created_by(d.pop("created_by", UNSET))

        def _parse_entity_type_hint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        entity_type_hint = _parse_entity_type_hint(d.pop("entity_type_hint", UNSET))

        def _parse_file_format(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_format = _parse_file_format(d.pop("file_format", UNSET))

        def _parse_file_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        file_name = _parse_file_name(d.pop("file_name", UNSET))

        def _parse_org_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        def _parse_source_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_label = _parse_source_label(d.pop("source_label", UNSET))

        total_rows = d.pop("total_rows", UNSET)

        import_batch_response = cls(
            domain_id=domain_id,
            id=id,
            source_type=source_type,
            created_at=created_at,
            created_by=created_by,
            entity_type_hint=entity_type_hint,
            file_format=file_format,
            file_name=file_name,
            org_id=org_id,
            source_label=source_label,
            total_rows=total_rows,
        )

        import_batch_response.additional_properties = d
        return import_batch_response

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
