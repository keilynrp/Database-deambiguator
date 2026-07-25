from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_config import WidgetConfig


T = TypeVar("T", bound="DashboardCreate")


@_attrs_define
class DashboardCreate:
    """
    Attributes:
        name (str):
        layout (list[WidgetConfig] | Unset):
    """

    name: str
    layout: list[WidgetConfig] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        layout: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.layout, Unset):
            layout = []
            for layout_item_data in self.layout:
                layout_item = layout_item_data.to_dict()
                layout.append(layout_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if layout is not UNSET:
            field_dict["layout"] = layout

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_config import WidgetConfig

        d = dict(src_dict)
        name = d.pop("name")

        _layout = d.pop("layout", UNSET)
        layout: list[WidgetConfig] | Unset = UNSET
        if _layout is not UNSET:
            layout = []
            for layout_item_data in _layout:
                layout_item = WidgetConfig.from_dict(layout_item_data)

                layout.append(layout_item)

        dashboard_create = cls(
            name=name,
            layout=layout,
        )

        dashboard_create.additional_properties = d
        return dashboard_create

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
