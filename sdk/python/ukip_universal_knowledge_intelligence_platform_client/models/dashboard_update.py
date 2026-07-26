from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_config import WidgetConfig


T = TypeVar("T", bound="DashboardUpdate")


@_attrs_define
class DashboardUpdate:
    """
    Attributes:
        layout (list[WidgetConfig] | None | Unset):
        name (None | str | Unset):
    """

    layout: list[WidgetConfig] | None | Unset = UNSET
    name: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        layout: list[dict[str, Any]] | None | Unset
        if isinstance(self.layout, Unset):
            layout = UNSET
        elif isinstance(self.layout, list):
            layout = []
            for layout_type_0_item_data in self.layout:
                layout_type_0_item = layout_type_0_item_data.to_dict()
                layout.append(layout_type_0_item)

        else:
            layout = self.layout

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if layout is not UNSET:
            field_dict["layout"] = layout
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_config import WidgetConfig

        d = dict(src_dict)

        def _parse_layout(data: object) -> list[WidgetConfig] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                layout_type_0 = []
                _layout_type_0 = data
                for layout_type_0_item_data in _layout_type_0:
                    layout_type_0_item = WidgetConfig.from_dict(layout_type_0_item_data)

                    layout_type_0.append(layout_type_0_item)

                return layout_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[WidgetConfig] | None | Unset, data)

        layout = _parse_layout(d.pop("layout", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        dashboard_update = cls(
            layout=layout,
            name=name,
        )

        dashboard_update.additional_properties = d
        return dashboard_update

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
