from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LegacyAffiliationFixResponse")


@_attrs_define
class LegacyAffiliationFixResponse:
    """Counter shape returned by the backfill script.

    Attributes:
        fixed (int): Entities whose attributes_json.affiliation was cleared.
        matched (int): Entities whose enrichment_source matched the affected providers.
        mode (str): 'dry-run' or 'applied'
        requeue_enrichment (bool):
        scanned (int): Total entities visited under the filter.
    """

    fixed: int
    matched: int
    mode: str
    requeue_enrichment: bool
    scanned: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        fixed = self.fixed

        matched = self.matched

        mode = self.mode

        requeue_enrichment = self.requeue_enrichment

        scanned = self.scanned

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fixed": fixed,
                "matched": matched,
                "mode": mode,
                "requeue_enrichment": requeue_enrichment,
                "scanned": scanned,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        fixed = d.pop("fixed")

        matched = d.pop("matched")

        mode = d.pop("mode")

        requeue_enrichment = d.pop("requeue_enrichment")

        scanned = d.pop("scanned")

        legacy_affiliation_fix_response = cls(
            fixed=fixed,
            matched=matched,
            mode=mode,
            requeue_enrichment=requeue_enrichment,
            scanned=scanned,
        )

        legacy_affiliation_fix_response.additional_properties = d
        return legacy_affiliation_fix_response

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
