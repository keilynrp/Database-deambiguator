from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.graph_edge import GraphEdge
    from ..models.graph_node import GraphNode


T = TypeVar("T", bound="EntityGraphResponse")


@_attrs_define
class EntityGraphResponse:
    """
    Attributes:
        center_id (int):
        depth (int):
        edges (list[GraphEdge]):
        nodes (list[GraphNode]):
    """

    center_id: int
    depth: int
    edges: list[GraphEdge]
    nodes: list[GraphNode]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        center_id = self.center_id

        depth = self.depth

        edges = []
        for edges_item_data in self.edges:
            edges_item = edges_item_data.to_dict()
            edges.append(edges_item)

        nodes = []
        for nodes_item_data in self.nodes:
            nodes_item = nodes_item_data.to_dict()
            nodes.append(nodes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "center_id": center_id,
                "depth": depth,
                "edges": edges,
                "nodes": nodes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_edge import GraphEdge
        from ..models.graph_node import GraphNode

        d = dict(src_dict)
        center_id = d.pop("center_id")

        depth = d.pop("depth")

        edges = []
        _edges = d.pop("edges")
        for edges_item_data in _edges:
            edges_item = GraphEdge.from_dict(edges_item_data)

            edges.append(edges_item)

        nodes = []
        _nodes = d.pop("nodes")
        for nodes_item_data in _nodes:
            nodes_item = GraphNode.from_dict(nodes_item_data)

            nodes.append(nodes_item)

        entity_graph_response = cls(
            center_id=center_id,
            depth=depth,
            edges=edges,
            nodes=nodes,
        )

        entity_graph_response.additional_properties = d
        return entity_graph_response

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
