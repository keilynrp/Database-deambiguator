from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnnotationCreate")


@_attrs_define
class AnnotationCreate:
    """
    Attributes:
        content (str):
        authority_id (int | None | Unset):
        entity_id (int | None | Unset):
        parent_id (int | None | Unset):
    """

    content: str
    authority_id: int | None | Unset = UNSET
    entity_id: int | None | Unset = UNSET
    parent_id: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        content = self.content

        authority_id: int | None | Unset
        if isinstance(self.authority_id, Unset):
            authority_id = UNSET
        else:
            authority_id = self.authority_id

        entity_id: int | None | Unset
        if isinstance(self.entity_id, Unset):
            entity_id = UNSET
        else:
            entity_id = self.entity_id

        parent_id: int | None | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        else:
            parent_id = self.parent_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
            }
        )
        if authority_id is not UNSET:
            field_dict["authority_id"] = authority_id
        if entity_id is not UNSET:
            field_dict["entity_id"] = entity_id
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        content = d.pop("content")

        def _parse_authority_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        authority_id = _parse_authority_id(d.pop("authority_id", UNSET))

        def _parse_entity_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        entity_id = _parse_entity_id(d.pop("entity_id", UNSET))

        def _parse_parent_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        parent_id = _parse_parent_id(d.pop("parent_id", UNSET))

        annotation_create = cls(
            content=content,
            authority_id=authority_id,
            entity_id=entity_id,
            parent_id=parent_id,
        )

        annotation_create.additional_properties = d
        return annotation_create

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
