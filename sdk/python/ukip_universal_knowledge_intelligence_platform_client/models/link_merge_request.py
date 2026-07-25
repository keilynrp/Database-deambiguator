from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LinkMergeRequest")


@_attrs_define
class LinkMergeRequest:
    """
    Attributes:
        primary_id (int):
        secondary_ids (list[int]):
        strategy (str | Unset):  Default: 'keep_non_empty'.
    """

    primary_id: int
    secondary_ids: list[int]
    strategy: str | Unset = "keep_non_empty"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        primary_id = self.primary_id

        secondary_ids = self.secondary_ids

        strategy = self.strategy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "primary_id": primary_id,
                "secondary_ids": secondary_ids,
            }
        )
        if strategy is not UNSET:
            field_dict["strategy"] = strategy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        primary_id = d.pop("primary_id")

        secondary_ids = cast(list[int], d.pop("secondary_ids"))

        strategy = d.pop("strategy", UNSET)

        link_merge_request = cls(
            primary_id=primary_id,
            secondary_ids=secondary_ids,
            strategy=strategy,
        )

        link_merge_request.additional_properties = d
        return link_merge_request

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
