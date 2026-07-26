from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FamilyCountsResponse")


@_attrs_define
class FamilyCountsResponse:
    """
    Attributes:
        extracted (int | Unset):  Default: 0.
        failed (int | Unset):  Default: 0.
        rejected (int | Unset):  Default: 0.
        resolved (int | Unset):  Default: 0.
        review_required (int | Unset):  Default: 0.
        stale (int | Unset):  Default: 0.
    """

    extracted: int | Unset = 0
    failed: int | Unset = 0
    rejected: int | Unset = 0
    resolved: int | Unset = 0
    review_required: int | Unset = 0
    stale: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        extracted = self.extracted

        failed = self.failed

        rejected = self.rejected

        resolved = self.resolved

        review_required = self.review_required

        stale = self.stale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if extracted is not UNSET:
            field_dict["extracted"] = extracted
        if failed is not UNSET:
            field_dict["failed"] = failed
        if rejected is not UNSET:
            field_dict["rejected"] = rejected
        if resolved is not UNSET:
            field_dict["resolved"] = resolved
        if review_required is not UNSET:
            field_dict["review_required"] = review_required
        if stale is not UNSET:
            field_dict["stale"] = stale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        extracted = d.pop("extracted", UNSET)

        failed = d.pop("failed", UNSET)

        rejected = d.pop("rejected", UNSET)

        resolved = d.pop("resolved", UNSET)

        review_required = d.pop("review_required", UNSET)

        stale = d.pop("stale", UNSET)

        family_counts_response = cls(
            extracted=extracted,
            failed=failed,
            rejected=rejected,
            resolved=resolved,
            review_required=review_required,
            stale=stale,
        )

        family_counts_response.additional_properties = d
        return family_counts_response

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
