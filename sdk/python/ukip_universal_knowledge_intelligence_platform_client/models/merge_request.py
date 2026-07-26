from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="MergeRequest")


@_attrs_define
class MergeRequest:
    """
    Attributes:
        loser_id (int): Entity to absorb then delete
        winner_id (int): Entity to keep
    """

    loser_id: int
    winner_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        loser_id = self.loser_id

        winner_id = self.winner_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "loser_id": loser_id,
                "winner_id": winner_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        loser_id = d.pop("loser_id")

        winner_id = d.pop("winner_id")

        merge_request = cls(
            loser_id=loser_id,
            winner_id=winner_id,
        )

        merge_request.additional_properties = d
        return merge_request

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
