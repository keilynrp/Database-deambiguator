from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceApplyPayload")


@_attrs_define
class FieldCorrespondenceApplyPayload:
    """
    Attributes:
        dry_run (bool | Unset):  Default: True.
        limit (int | Unset):  Default: 5000.
        overwrite_existing (bool | Unset):  Default: False.
    """

    dry_run: bool | Unset = True
    limit: int | Unset = 5000
    overwrite_existing: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dry_run = self.dry_run

        limit = self.limit

        overwrite_existing = self.overwrite_existing

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if dry_run is not UNSET:
            field_dict["dry_run"] = dry_run
        if limit is not UNSET:
            field_dict["limit"] = limit
        if overwrite_existing is not UNSET:
            field_dict["overwrite_existing"] = overwrite_existing

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        dry_run = d.pop("dry_run", UNSET)

        limit = d.pop("limit", UNSET)

        overwrite_existing = d.pop("overwrite_existing", UNSET)

        field_correspondence_apply_payload = cls(
            dry_run=dry_run,
            limit=limit,
            overwrite_existing=overwrite_existing,
        )

        field_correspondence_apply_payload.additional_properties = d
        return field_correspondence_apply_payload

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
