from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EntityRelationshipResponse")


@_attrs_define
class EntityRelationshipResponse:
    """
    Attributes:
        created_at (datetime.datetime):
        id (int):
        notes (None | str):
        relation_type (str):
        source_id (int):
        target_id (int):
        weight (float):
    """

    created_at: datetime.datetime
    id: int
    notes: None | str
    relation_type: str
    source_id: int
    target_id: int
    weight: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        id = self.id

        notes: None | str
        notes = self.notes

        relation_type = self.relation_type

        source_id = self.source_id

        target_id = self.target_id

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "id": id,
                "notes": notes,
                "relation_type": relation_type,
                "source_id": source_id,
                "target_id": target_id,
                "weight": weight,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        id = d.pop("id")

        def _parse_notes(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        notes = _parse_notes(d.pop("notes"))

        relation_type = d.pop("relation_type")

        source_id = d.pop("source_id")

        target_id = d.pop("target_id")

        weight = d.pop("weight")

        entity_relationship_response = cls(
            created_at=created_at,
            id=id,
            notes=notes,
            relation_type=relation_type,
            source_id=source_id,
            target_id=target_id,
            weight=weight,
        )

        entity_relationship_response.additional_properties = d
        return entity_relationship_response

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
