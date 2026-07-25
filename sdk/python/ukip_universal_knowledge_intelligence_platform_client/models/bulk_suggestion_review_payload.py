from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BulkSuggestionReviewPayload")


@_attrs_define
class BulkSuggestionReviewPayload:
    """
    Attributes:
        suggestion_ids (list[int]):
        rationale (None | str | Unset):
    """

    suggestion_ids: list[int]
    rationale: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        suggestion_ids = self.suggestion_ids

        rationale: None | str | Unset
        if isinstance(self.rationale, Unset):
            rationale = UNSET
        else:
            rationale = self.rationale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "suggestion_ids": suggestion_ids,
            }
        )
        if rationale is not UNSET:
            field_dict["rationale"] = rationale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        suggestion_ids = cast(list[int], d.pop("suggestion_ids"))

        def _parse_rationale(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rationale = _parse_rationale(d.pop("rationale", UNSET))

        bulk_suggestion_review_payload = cls(
            suggestion_ids=suggestion_ids,
            rationale=rationale,
        )

        bulk_suggestion_review_payload.additional_properties = d
        return bulk_suggestion_review_payload

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
