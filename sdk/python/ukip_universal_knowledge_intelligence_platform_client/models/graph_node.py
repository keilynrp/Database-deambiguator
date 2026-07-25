from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GraphNode")


@_attrs_define
class GraphNode:
    """
    Attributes:
        domain (None | str):
        entity_type (None | str):
        id (int):
        is_center (bool):
        label (str):
    """

    domain: None | str
    entity_type: None | str
    id: int
    is_center: bool
    label: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain: None | str
        domain = self.domain

        entity_type: None | str
        entity_type = self.entity_type

        id = self.id

        is_center = self.is_center

        label = self.label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain": domain,
                "entity_type": entity_type,
                "id": id,
                "is_center": is_center,
                "label": label,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_domain(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        domain = _parse_domain(d.pop("domain"))

        def _parse_entity_type(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        entity_type = _parse_entity_type(d.pop("entity_type"))

        id = d.pop("id")

        is_center = d.pop("is_center")

        label = d.pop("label")

        graph_node = cls(
            domain=domain,
            entity_type=entity_type,
            id=id,
            is_center=is_center,
            label=label,
        )

        graph_node.additional_properties = d
        return graph_node

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
