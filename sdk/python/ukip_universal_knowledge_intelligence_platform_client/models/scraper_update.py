from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.scraper_update_field_map_type_0 import ScraperUpdateFieldMapType0


T = TypeVar("T", bound="ScraperUpdate")


@_attrs_define
class ScraperUpdate:
    """
    Attributes:
        field_map (None | ScraperUpdateFieldMapType0 | Unset):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        rate_limit_secs (float | None | Unset):
        selector (None | str | Unset):
        selector_type (None | str | Unset):
        url_template (None | str | Unset):
    """

    field_map: None | ScraperUpdateFieldMapType0 | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    rate_limit_secs: float | None | Unset = UNSET
    selector: None | str | Unset = UNSET
    selector_type: None | str | Unset = UNSET
    url_template: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.scraper_update_field_map_type_0 import ScraperUpdateFieldMapType0

        field_map: dict[str, Any] | None | Unset
        if isinstance(self.field_map, Unset):
            field_map = UNSET
        elif isinstance(self.field_map, ScraperUpdateFieldMapType0):
            field_map = self.field_map.to_dict()
        else:
            field_map = self.field_map

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

        rate_limit_secs: float | None | Unset
        if isinstance(self.rate_limit_secs, Unset):
            rate_limit_secs = UNSET
        else:
            rate_limit_secs = self.rate_limit_secs

        selector: None | str | Unset
        if isinstance(self.selector, Unset):
            selector = UNSET
        else:
            selector = self.selector

        selector_type: None | str | Unset
        if isinstance(self.selector_type, Unset):
            selector_type = UNSET
        else:
            selector_type = self.selector_type

        url_template: None | str | Unset
        if isinstance(self.url_template, Unset):
            url_template = UNSET
        else:
            url_template = self.url_template

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if field_map is not UNSET:
            field_dict["field_map"] = field_map
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if rate_limit_secs is not UNSET:
            field_dict["rate_limit_secs"] = rate_limit_secs
        if selector is not UNSET:
            field_dict["selector"] = selector
        if selector_type is not UNSET:
            field_dict["selector_type"] = selector_type
        if url_template is not UNSET:
            field_dict["url_template"] = url_template

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.scraper_update_field_map_type_0 import ScraperUpdateFieldMapType0

        d = dict(src_dict)

        def _parse_field_map(data: object) -> None | ScraperUpdateFieldMapType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_map_type_0 = ScraperUpdateFieldMapType0.from_dict(data)

                return field_map_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ScraperUpdateFieldMapType0 | Unset, data)

        field_map = _parse_field_map(d.pop("field_map", UNSET))

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

        def _parse_rate_limit_secs(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        rate_limit_secs = _parse_rate_limit_secs(d.pop("rate_limit_secs", UNSET))

        def _parse_selector(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        selector = _parse_selector(d.pop("selector", UNSET))

        def _parse_selector_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        selector_type = _parse_selector_type(d.pop("selector_type", UNSET))

        def _parse_url_template(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url_template = _parse_url_template(d.pop("url_template", UNSET))

        scraper_update = cls(
            field_map=field_map,
            is_active=is_active,
            name=name,
            rate_limit_secs=rate_limit_secs,
            selector=selector,
            selector_type=selector_type,
            url_template=url_template,
        )

        scraper_update.additional_properties = d
        return scraper_update

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
