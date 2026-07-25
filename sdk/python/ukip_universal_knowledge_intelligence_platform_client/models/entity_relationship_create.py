from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntityRelationshipCreate")


@_attrs_define
class EntityRelationshipCreate:
    """
    Attributes:
        relation_type (str):
        target_id (int):
        notes (None | str | Unset):
        weight (float | Unset):  Default: 1.0.
    """

    relation_type: str
    target_id: int
    notes: None | str | Unset = UNSET
    weight: float | Unset = 1.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        relation_type = self.relation_type

        target_id = self.target_id

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "relation_type": relation_type,
                "target_id": target_id,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        relation_type = d.pop("relation_type")

        target_id = d.pop("target_id")

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        weight = d.pop("weight", UNSET)

        entity_relationship_create = cls(
            relation_type=relation_type,
            target_id=target_id,
            notes=notes,
            weight=weight,
        )

        entity_relationship_create.additional_properties = d
        return entity_relationship_create

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
