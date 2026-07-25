from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CanonicalIdentityFixResponse")


@_attrs_define
class CanonicalIdentityFixResponse:
    """Counter shape returned by the canonical identity backfill script.

    Attributes:
        fixed_canonical_id (int): Entities whose canonical_id was populated.
        fixed_entity_type (int): Entities whose entity_type was populated.
        mode (str): 'dry-run' or 'applied'
        scanned (int): Total entities visited under the filter.
        skipped_duplicates (int): Rows skipped to avoid canonical uniqueness collisions.
    """

    fixed_canonical_id: int
    fixed_entity_type: int
    mode: str
    scanned: int
    skipped_duplicates: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fixed_canonical_id = self.fixed_canonical_id

        fixed_entity_type = self.fixed_entity_type

        mode = self.mode

        scanned = self.scanned

        skipped_duplicates = self.skipped_duplicates

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fixed_canonical_id": fixed_canonical_id,
                "fixed_entity_type": fixed_entity_type,
                "mode": mode,
                "scanned": scanned,
                "skipped_duplicates": skipped_duplicates,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fixed_canonical_id = d.pop("fixed_canonical_id")

        fixed_entity_type = d.pop("fixed_entity_type")

        mode = d.pop("mode")

        scanned = d.pop("scanned")

        skipped_duplicates = d.pop("skipped_duplicates")

        canonical_identity_fix_response = cls(
            fixed_canonical_id=fixed_canonical_id,
            fixed_entity_type=fixed_entity_type,
            mode=mode,
            scanned=scanned,
            skipped_duplicates=skipped_duplicates,
        )

        canonical_identity_fix_response.additional_properties = d
        return canonical_identity_fix_response

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
