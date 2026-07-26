from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.widget_config_config import WidgetConfigConfig


T = TypeVar("T", bound="WidgetConfig")


@_attrs_define
class WidgetConfig:
    """
    Attributes:
        id (str):
        type_ (str):
        cols (int | Unset):  Default: 6.
        config (WidgetConfigConfig | Unset):
        title (None | str | Unset):
    """

    id: str
    type_: str
    cols: int | Unset = 6
    config: WidgetConfigConfig | Unset = UNSET
    title: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_ = self.type_

        cols = self.cols

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "type": type_,
            }
        )
        if cols is not UNSET:
            field_dict["cols"] = cols
        if config is not UNSET:
            field_dict["config"] = config
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.widget_config_config import WidgetConfigConfig

        d = dict(src_dict)
        id = d.pop("id")

        type_ = d.pop("type")

        cols = d.pop("cols", UNSET)

        _config = d.pop("config", UNSET)
        config: WidgetConfigConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = WidgetConfigConfig.from_dict(_config)

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        widget_config = cls(
            id=id,
            type_=type_,
            cols=cols,
            config=config,
            title=title,
        )

        widget_config.additional_properties = d
        return widget_config

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
