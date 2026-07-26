from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.entity_snap import EntitySnap


T = TypeVar("T", bound="LinkCandidateResponse")


@_attrs_define
class LinkCandidateResponse:
    """
    Attributes:
        entity_a (EntitySnap):
        entity_b (EntitySnap):
        matched_fields (list[str]):
        score (float):
    """

    entity_a: EntitySnap
    entity_b: EntitySnap
    matched_fields: list[str]
    score: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_a = self.entity_a.to_dict()

        entity_b = self.entity_b.to_dict()

        matched_fields = self.matched_fields

        score = self.score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_a": entity_a,
                "entity_b": entity_b,
                "matched_fields": matched_fields,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.entity_snap import EntitySnap

        d = dict(src_dict)
        entity_a = EntitySnap.from_dict(d.pop("entity_a"))

        entity_b = EntitySnap.from_dict(d.pop("entity_b"))

        matched_fields = cast(list[str], d.pop("matched_fields"))

        score = d.pop("score")

        link_candidate_response = cls(
            entity_a=entity_a,
            entity_b=entity_b,
            matched_fields=matched_fields,
            score=score,
        )

        link_candidate_response.additional_properties = d
        return link_candidate_response

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
