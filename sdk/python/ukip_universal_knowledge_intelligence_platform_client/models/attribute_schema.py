from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttributeSchema")


@_attrs_define
class AttributeSchema:
    """
    Attributes:
        label (str):
        name (str):
        type_ (str):
        is_core (bool | Unset):  Default: False.
        item_key (None | str | Unset):
        multi_valued (bool | Unset):  Default: False.
        required (bool | Unset):  Default: False.
        separator (str | Unset):  Default: ', '.
        source (None | str | Unset):
    """

    label: str
    name: str
    type_: str
    is_core: bool | Unset = False
    item_key: None | str | Unset = UNSET
    multi_valued: bool | Unset = False
    required: bool | Unset = False
    separator: str | Unset = ", "
    source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        name = self.name

        type_ = self.type_

        is_core = self.is_core

        item_key: None | str | Unset
        if isinstance(self.item_key, Unset):
            item_key = UNSET
        else:
            item_key = self.item_key

        multi_valued = self.multi_valued

        required = self.required

        separator = self.separator

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
                "name": name,
                "type": type_,
            }
        )
        if is_core is not UNSET:
            field_dict["is_core"] = is_core
        if item_key is not UNSET:
            field_dict["item_key"] = item_key
        if multi_valued is not UNSET:
            field_dict["multi_valued"] = multi_valued
        if required is not UNSET:
            field_dict["required"] = required
        if separator is not UNSET:
            field_dict["separator"] = separator
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        name = d.pop("name")

        type_ = d.pop("type")

        is_core = d.pop("is_core", UNSET)

        def _parse_item_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        item_key = _parse_item_key(d.pop("item_key", UNSET))

        multi_valued = d.pop("multi_valued", UNSET)

        required = d.pop("required", UNSET)

        separator = d.pop("separator", UNSET)

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        attribute_schema = cls(
            label=label,
            name=name,
            type_=type_,
            is_core=is_core,
            item_key=item_key,
            multi_valued=multi_valued,
            required=required,
            separator=separator,
            source=source,
        )

        attribute_schema.additional_properties = d
        return attribute_schema

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
