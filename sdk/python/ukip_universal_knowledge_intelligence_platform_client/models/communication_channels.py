from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.channel_tier import ChannelTier


T = TypeVar("T", bound="CommunicationChannels")


@_attrs_define
class CommunicationChannels:
    """
    Attributes:
        tier_1 (ChannelTier | None | Unset):
        tier_2 (ChannelTier | None | Unset):
        tier_3 (ChannelTier | None | Unset):
    """

    tier_1: ChannelTier | None | Unset = UNSET
    tier_2: ChannelTier | None | Unset = UNSET
    tier_3: ChannelTier | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.channel_tier import ChannelTier

        tier_1: dict[str, Any] | None | Unset
        if isinstance(self.tier_1, Unset):
            tier_1 = UNSET
        elif isinstance(self.tier_1, ChannelTier):
            tier_1 = self.tier_1.to_dict()
        else:
            tier_1 = self.tier_1

        tier_2: dict[str, Any] | None | Unset
        if isinstance(self.tier_2, Unset):
            tier_2 = UNSET
        elif isinstance(self.tier_2, ChannelTier):
            tier_2 = self.tier_2.to_dict()
        else:
            tier_2 = self.tier_2

        tier_3: dict[str, Any] | None | Unset
        if isinstance(self.tier_3, Unset):
            tier_3 = UNSET
        elif isinstance(self.tier_3, ChannelTier):
            tier_3 = self.tier_3.to_dict()
        else:
            tier_3 = self.tier_3

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tier_1 is not UNSET:
            field_dict["tier_1"] = tier_1
        if tier_2 is not UNSET:
            field_dict["tier_2"] = tier_2
        if tier_3 is not UNSET:
            field_dict["tier_3"] = tier_3

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.channel_tier import ChannelTier

        d = dict(src_dict)

        def _parse_tier_1(data: object) -> ChannelTier | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tier_1_type_0 = ChannelTier.from_dict(data)

                return tier_1_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChannelTier | None | Unset, data)

        tier_1 = _parse_tier_1(d.pop("tier_1", UNSET))

        def _parse_tier_2(data: object) -> ChannelTier | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tier_2_type_0 = ChannelTier.from_dict(data)

                return tier_2_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChannelTier | None | Unset, data)

        tier_2 = _parse_tier_2(d.pop("tier_2", UNSET))

        def _parse_tier_3(data: object) -> ChannelTier | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tier_3_type_0 = ChannelTier.from_dict(data)

                return tier_3_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ChannelTier | None | Unset, data)

        tier_3 = _parse_tier_3(d.pop("tier_3", UNSET))

        communication_channels = cls(
            tier_1=tier_1,
            tier_2=tier_2,
            tier_3=tier_3,
        )

        communication_channels.additional_properties = d
        return communication_channels

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
