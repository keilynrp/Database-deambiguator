from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.paradigm_indicators import ParadigmIndicators


T = TypeVar("T", bound="Paradigm")


@_attrs_define
class Paradigm:
    """
    Attributes:
        id (str):
        label (str):
        description (str | Unset):  Default: ''.
        indicators (ParadigmIndicators | Unset):
    """

    id: str
    label: str
    description: str | Unset = ""
    indicators: ParadigmIndicators | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        label = self.label

        description = self.description

        indicators: dict[str, Any] | Unset = UNSET
        if not isinstance(self.indicators, Unset):
            indicators = self.indicators.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "label": label,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if indicators is not UNSET:
            field_dict["indicators"] = indicators

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.paradigm_indicators import ParadigmIndicators

        d = dict(src_dict)
        id = d.pop("id")

        label = d.pop("label")

        description = d.pop("description", UNSET)

        _indicators = d.pop("indicators", UNSET)
        indicators: ParadigmIndicators | Unset
        if isinstance(_indicators, Unset):
            indicators = UNSET
        else:
            indicators = ParadigmIndicators.from_dict(_indicators)

        paradigm = cls(
            id=id,
            label=label,
            description=description,
            indicators=indicators,
        )

        paradigm.additional_properties = d
        return paradigm

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
