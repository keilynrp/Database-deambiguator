from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkImportResponse")


@_attrs_define
class BulkImportResponse:
    """
    Attributes:
        entities_updated (int):
        imported (int):
        skipped (int):
        warnings (list[str] | Unset):
    """

    entities_updated: int
    imported: int
    skipped: int
    warnings: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entities_updated = self.entities_updated

        imported = self.imported

        skipped = self.skipped

        warnings: list[str] | Unset = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = self.warnings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entities_updated": entities_updated,
                "imported": imported,
                "skipped": skipped,
            }
        )
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entities_updated = d.pop("entities_updated")

        imported = d.pop("imported")

        skipped = d.pop("skipped")

        warnings = cast(list[str], d.pop("warnings", UNSET))

        bulk_import_response = cls(
            entities_updated=entities_updated,
            imported=imported,
            skipped=skipped,
            warnings=warnings,
        )

        bulk_import_response.additional_properties = d
        return bulk_import_response

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
