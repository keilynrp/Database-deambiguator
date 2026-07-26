from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelTier")


@_attrs_define
class ChannelTier:
    """
    Attributes:
        label (str):
        auto_detect (bool | Unset):  Default: False.
        description (str | Unset):  Default: ''.
        manual_seeds (list[str] | Unset):
    """

    label: str
    auto_detect: bool | Unset = False
    description: str | Unset = ""
    manual_seeds: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        auto_detect = self.auto_detect

        description = self.description

        manual_seeds: list[str] | Unset = UNSET
        if not isinstance(self.manual_seeds, Unset):
            manual_seeds = self.manual_seeds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
            }
        )
        if auto_detect is not UNSET:
            field_dict["auto_detect"] = auto_detect
        if description is not UNSET:
            field_dict["description"] = description
        if manual_seeds is not UNSET:
            field_dict["manual_seeds"] = manual_seeds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        auto_detect = d.pop("auto_detect", UNSET)

        description = d.pop("description", UNSET)

        manual_seeds = cast(list[str], d.pop("manual_seeds", UNSET))

        channel_tier = cls(
            label=label,
            auto_detect=auto_detect,
            description=description,
            manual_seeds=manual_seeds,
        )

        channel_tier.additional_properties = d
        return channel_tier

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
