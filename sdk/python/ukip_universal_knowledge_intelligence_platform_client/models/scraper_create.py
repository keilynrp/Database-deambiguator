from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.scraper_create_field_map import ScraperCreateFieldMap


T = TypeVar("T", bound="ScraperCreate")


@_attrs_define
class ScraperCreate:
    """
    Attributes:
        name (str):
        selector (str):
        url_template (str):
        field_map (ScraperCreateFieldMap | Unset):
        is_active (bool | Unset):  Default: True.
        rate_limit_secs (float | Unset):  Default: 1.0.
        selector_type (str | Unset):  Default: 'css'.
    """

    name: str
    selector: str
    url_template: str
    field_map: ScraperCreateFieldMap | Unset = UNSET
    is_active: bool | Unset = True
    rate_limit_secs: float | Unset = 1.0
    selector_type: str | Unset = "css"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        selector = self.selector

        url_template = self.url_template

        field_map: dict[str, Any] | Unset = UNSET
        if not isinstance(self.field_map, Unset):
            field_map = self.field_map.to_dict()

        is_active = self.is_active

        rate_limit_secs = self.rate_limit_secs

        selector_type = self.selector_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "selector": selector,
                "url_template": url_template,
            }
        )
        if field_map is not UNSET:
            field_dict["field_map"] = field_map
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if rate_limit_secs is not UNSET:
            field_dict["rate_limit_secs"] = rate_limit_secs
        if selector_type is not UNSET:
            field_dict["selector_type"] = selector_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scraper_create_field_map import ScraperCreateFieldMap

        d = dict(src_dict)
        name = d.pop("name")

        selector = d.pop("selector")

        url_template = d.pop("url_template")

        _field_map = d.pop("field_map", UNSET)
        field_map: ScraperCreateFieldMap | Unset
        if isinstance(_field_map, Unset):
            field_map = UNSET
        else:
            field_map = ScraperCreateFieldMap.from_dict(_field_map)

        is_active = d.pop("is_active", UNSET)

        rate_limit_secs = d.pop("rate_limit_secs", UNSET)

        selector_type = d.pop("selector_type", UNSET)

        scraper_create = cls(
            name=name,
            selector=selector,
            url_template=url_template,
            field_map=field_map,
            is_active=is_active,
            rate_limit_secs=rate_limit_secs,
            selector_type=selector_type,
        )

        scraper_create.additional_properties = d
        return scraper_create

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
