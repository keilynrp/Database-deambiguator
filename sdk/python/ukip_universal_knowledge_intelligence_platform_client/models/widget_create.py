from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_create_config import WidgetCreateConfig


T = TypeVar("T", bound="WidgetCreate")


@_attrs_define
class WidgetCreate:
    """
    Attributes:
        name (str):
        widget_type (str):
        allowed_origins (str | Unset):  Default: '*'.
        config (WidgetCreateConfig | Unset):
        is_active (bool | Unset):  Default: True.
    """

    name: str
    widget_type: str
    allowed_origins: str | Unset = "*"
    config: WidgetCreateConfig | Unset = UNSET
    is_active: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        widget_type = self.widget_type

        allowed_origins = self.allowed_origins

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        is_active = self.is_active

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "widget_type": widget_type,
            }
        )
        if allowed_origins is not UNSET:
            field_dict["allowed_origins"] = allowed_origins
        if config is not UNSET:
            field_dict["config"] = config
        if is_active is not UNSET:
            field_dict["is_active"] = is_active

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_create_config import WidgetCreateConfig

        d = dict(src_dict)
        name = d.pop("name")

        widget_type = d.pop("widget_type")

        allowed_origins = d.pop("allowed_origins", UNSET)

        _config = d.pop("config", UNSET)
        config: WidgetCreateConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = WidgetCreateConfig.from_dict(_config)

        is_active = d.pop("is_active", UNSET)

        widget_create = cls(
            name=name,
            widget_type=widget_type,
            allowed_origins=allowed_origins,
            config=config,
            is_active=is_active,
        )

        widget_create.additional_properties = d
        return widget_create

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
