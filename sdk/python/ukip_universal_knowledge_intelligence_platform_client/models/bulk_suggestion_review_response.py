from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkSuggestionReviewResponse")


@_attrs_define
class BulkSuggestionReviewResponse:
    """
    Attributes:
        action (str):
        reviewed (int):
        not_found (list[int] | Unset):
    """

    action: str
    reviewed: int
    not_found: list[int] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action

        reviewed = self.reviewed

        not_found: list[int] | Unset = UNSET
        if not isinstance(self.not_found, Unset):
            not_found = self.not_found

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "reviewed": reviewed,
            }
        )
        if not_found is not UNSET:
            field_dict["not_found"] = not_found

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action = d.pop("action")

        reviewed = d.pop("reviewed")

        not_found = cast(list[int], d.pop("not_found", UNSET))

        bulk_suggestion_review_response = cls(
            action=action,
            reviewed=reviewed,
            not_found=not_found,
        )

        bulk_suggestion_review_response.additional_properties = d
        return bulk_suggestion_review_response

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
