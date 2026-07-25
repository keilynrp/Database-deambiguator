from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SecretRotationEventResponse")


@_attrs_define
class SecretRotationEventResponse:
    """
    Attributes:
        id (int):
        operator (str):
        rotated_at (datetime.datetime):
        secret_name (str):
        new_key_fingerprint (None | str | Unset):
        notes (None | str | Unset):
        old_key_fingerprint (None | str | Unset):
        rows_reencrypted (int | None | Unset):
    """

    id: int
    operator: str
    rotated_at: datetime.datetime
    secret_name: str
    new_key_fingerprint: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    old_key_fingerprint: None | str | Unset = UNSET
    rows_reencrypted: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        operator = self.operator

        rotated_at = self.rotated_at.isoformat()

        secret_name = self.secret_name

        new_key_fingerprint: None | str | Unset
        if isinstance(self.new_key_fingerprint, Unset):
            new_key_fingerprint = UNSET
        else:
            new_key_fingerprint = self.new_key_fingerprint

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        old_key_fingerprint: None | str | Unset
        if isinstance(self.old_key_fingerprint, Unset):
            old_key_fingerprint = UNSET
        else:
            old_key_fingerprint = self.old_key_fingerprint

        rows_reencrypted: int | None | Unset
        if isinstance(self.rows_reencrypted, Unset):
            rows_reencrypted = UNSET
        else:
            rows_reencrypted = self.rows_reencrypted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "operator": operator,
                "rotated_at": rotated_at,
                "secret_name": secret_name,
            }
        )
        if new_key_fingerprint is not UNSET:
            field_dict["new_key_fingerprint"] = new_key_fingerprint
        if notes is not UNSET:
            field_dict["notes"] = notes
        if old_key_fingerprint is not UNSET:
            field_dict["old_key_fingerprint"] = old_key_fingerprint
        if rows_reencrypted is not UNSET:
            field_dict["rows_reencrypted"] = rows_reencrypted

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        operator = d.pop("operator")

        rotated_at = datetime.datetime.fromisoformat(d.pop("rotated_at"))

        secret_name = d.pop("secret_name")

        def _parse_new_key_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        new_key_fingerprint = _parse_new_key_fingerprint(d.pop("new_key_fingerprint", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_old_key_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        old_key_fingerprint = _parse_old_key_fingerprint(d.pop("old_key_fingerprint", UNSET))

        def _parse_rows_reencrypted(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        rows_reencrypted = _parse_rows_reencrypted(d.pop("rows_reencrypted", UNSET))

        secret_rotation_event_response = cls(
            id=id,
            operator=operator,
            rotated_at=rotated_at,
            secret_name=secret_name,
            new_key_fingerprint=new_key_fingerprint,
            notes=notes,
            old_key_fingerprint=old_key_fingerprint,
            rows_reencrypted=rows_reencrypted,
        )

        secret_rotation_event_response.additional_properties = d
        return secret_rotation_event_response

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
