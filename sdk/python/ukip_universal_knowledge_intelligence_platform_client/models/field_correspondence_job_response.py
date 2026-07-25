from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceJobResponse")


@_attrs_define
class FieldCorrespondenceJobResponse:
    """
    Attributes:
        id (int):
        records_updated (int):
        affected_records (int | Unset):  Default: 0.
        executed_at (None | str | Unset):
        fields_modified (list[str] | Unset):
        reverted (bool | Unset):  Default: False.
        rule_id (int | None | Unset):
        rule_label (None | str | Unset):
        skipped_existing (int | Unset):  Default: 0.
        skipped_missing_value (int | Unset):  Default: 0.
        username (None | str | Unset):
    """

    id: int
    records_updated: int
    affected_records: int | Unset = 0
    executed_at: None | str | Unset = UNSET
    fields_modified: list[str] | Unset = UNSET
    reverted: bool | Unset = False
    rule_id: int | None | Unset = UNSET
    rule_label: None | str | Unset = UNSET
    skipped_existing: int | Unset = 0
    skipped_missing_value: int | Unset = 0
    username: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        records_updated = self.records_updated

        affected_records = self.affected_records

        executed_at: None | str | Unset
        if isinstance(self.executed_at, Unset):
            executed_at = UNSET
        else:
            executed_at = self.executed_at

        fields_modified: list[str] | Unset = UNSET
        if not isinstance(self.fields_modified, Unset):
            fields_modified = self.fields_modified

        reverted = self.reverted

        rule_id: int | None | Unset
        if isinstance(self.rule_id, Unset):
            rule_id = UNSET
        else:
            rule_id = self.rule_id

        rule_label: None | str | Unset
        if isinstance(self.rule_label, Unset):
            rule_label = UNSET
        else:
            rule_label = self.rule_label

        skipped_existing = self.skipped_existing

        skipped_missing_value = self.skipped_missing_value

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "records_updated": records_updated,
            }
        )
        if affected_records is not UNSET:
            field_dict["affected_records"] = affected_records
        if executed_at is not UNSET:
            field_dict["executed_at"] = executed_at
        if fields_modified is not UNSET:
            field_dict["fields_modified"] = fields_modified
        if reverted is not UNSET:
            field_dict["reverted"] = reverted
        if rule_id is not UNSET:
            field_dict["rule_id"] = rule_id
        if rule_label is not UNSET:
            field_dict["rule_label"] = rule_label
        if skipped_existing is not UNSET:
            field_dict["skipped_existing"] = skipped_existing
        if skipped_missing_value is not UNSET:
            field_dict["skipped_missing_value"] = skipped_missing_value
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        records_updated = d.pop("records_updated")

        affected_records = d.pop("affected_records", UNSET)

        def _parse_executed_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        executed_at = _parse_executed_at(d.pop("executed_at", UNSET))

        fields_modified = cast(list[str], d.pop("fields_modified", UNSET))

        reverted = d.pop("reverted", UNSET)

        def _parse_rule_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        rule_id = _parse_rule_id(d.pop("rule_id", UNSET))

        def _parse_rule_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rule_label = _parse_rule_label(d.pop("rule_label", UNSET))

        skipped_existing = d.pop("skipped_existing", UNSET)

        skipped_missing_value = d.pop("skipped_missing_value", UNSET)

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        field_correspondence_job_response = cls(
            id=id,
            records_updated=records_updated,
            affected_records=affected_records,
            executed_at=executed_at,
            fields_modified=fields_modified,
            reverted=reverted,
            rule_id=rule_id,
            rule_label=rule_label,
            skipped_existing=skipped_existing,
            skipped_missing_value=skipped_missing_value,
            username=username,
        )

        field_correspondence_job_response.additional_properties = d
        return field_correspondence_job_response

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
