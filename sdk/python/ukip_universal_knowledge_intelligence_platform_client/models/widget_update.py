from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_update_config_type_0 import WidgetUpdateConfigType0


T = TypeVar("T", bound="WidgetUpdate")


@_attrs_define
class WidgetUpdate:
    """
    Attributes:
        allowed_origins (None | str | Unset):
        config (None | Unset | WidgetUpdateConfigType0):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        widget_type (None | str | Unset):
    """

    allowed_origins: None | str | Unset = UNSET
    config: None | Unset | WidgetUpdateConfigType0 = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    widget_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.widget_update_config_type_0 import WidgetUpdateConfigType0

        allowed_origins: None | str | Unset
        if isinstance(self.allowed_origins, Unset):
            allowed_origins = UNSET
        else:
            allowed_origins = self.allowed_origins

        config: dict[str, Any] | None | Unset
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, WidgetUpdateConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        widget_type: None | str | Unset
        if isinstance(self.widget_type, Unset):
            widget_type = UNSET
        else:
            widget_type = self.widget_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allowed_origins is not UNSET:
            field_dict["allowed_origins"] = allowed_origins
        if config is not UNSET:
            field_dict["config"] = config
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if widget_type is not UNSET:
            field_dict["widget_type"] = widget_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_update_config_type_0 import WidgetUpdateConfigType0

        d = dict(src_dict)

        def _parse_allowed_origins(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        allowed_origins = _parse_allowed_origins(d.pop("allowed_origins", UNSET))

        def _parse_config(data: object) -> None | Unset | WidgetUpdateConfigType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = WidgetUpdateConfigType0.from_dict(data)

                return config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WidgetUpdateConfigType0, data)

        config = _parse_config(d.pop("config", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_widget_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        widget_type = _parse_widget_type(d.pop("widget_type", UNSET))

        widget_update = cls(
            allowed_origins=allowed_origins,
            config=config,
            is_active=is_active,
            name=name,
            widget_type=widget_type,
        )

        widget_update.additional_properties = d
        return widget_update

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
