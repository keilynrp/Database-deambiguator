from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ParadigmIndicators")


@_attrs_define
class ParadigmIndicators:
    """
    Attributes:
        document_types (list[str] | Unset):
        journals_affinity (list[str] | Unset):
        terms (list[str] | Unset):
    """

    document_types: list[str] | Unset = UNSET
    journals_affinity: list[str] | Unset = UNSET
    terms: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        document_types: list[str] | Unset = UNSET
        if not isinstance(self.document_types, Unset):
            document_types = self.document_types

        journals_affinity: list[str] | Unset = UNSET
        if not isinstance(self.journals_affinity, Unset):
            journals_affinity = self.journals_affinity

        terms: list[str] | Unset = UNSET
        if not isinstance(self.terms, Unset):
            terms = self.terms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if document_types is not UNSET:
            field_dict["document_types"] = document_types
        if journals_affinity is not UNSET:
            field_dict["journals_affinity"] = journals_affinity
        if terms is not UNSET:
            field_dict["terms"] = terms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        document_types = cast(list[str], d.pop("document_types", UNSET))

        journals_affinity = cast(list[str], d.pop("journals_affinity", UNSET))

        terms = cast(list[str], d.pop("terms", UNSET))

        paradigm_indicators = cls(
            document_types=document_types,
            journals_affinity=journals_affinity,
            terms=terms,
        )

        paradigm_indicators.additional_properties = d
        return paradigm_indicators

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
