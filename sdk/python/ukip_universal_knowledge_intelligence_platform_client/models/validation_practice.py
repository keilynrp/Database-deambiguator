from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ValidationPractice")


@_attrs_define
class ValidationPractice:
    """
    Attributes:
        id (str):
        label (str):
        detectable (bool | Unset):  Default: False.
        field (None | str | Unset):
        indicators (list[str] | Unset):
        weight (float | Unset):  Default: 1.0.
    """

    id: str
    label: str
    detectable: bool | Unset = False
    field: None | str | Unset = UNSET
    indicators: list[str] | Unset = UNSET
    weight: float | Unset = 1.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        detectable = self.detectable

        field: None | str | Unset
        if isinstance(self.field, Unset):
            field = UNSET
        else:
            field = self.field

        indicators: list[str] | Unset = UNSET
        if not isinstance(self.indicators, Unset):
            indicators = self.indicators

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "label": label,
            }
        )
        if detectable is not UNSET:
            field_dict["detectable"] = detectable
        if field is not UNSET:
            field_dict["field"] = field
        if indicators is not UNSET:
            field_dict["indicators"] = indicators
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        detectable = d.pop("detectable", UNSET)

        def _parse_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        field = _parse_field(d.pop("field", UNSET))

        indicators = cast(list[str], d.pop("indicators", UNSET))

        weight = d.pop("weight", UNSET)

        validation_practice = cls(
            id=id,
            label=label,
            detectable=detectable,
            field=field,
            indicators=indicators,
            weight=weight,
        )

        validation_practice.additional_properties = d
        return validation_practice

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
