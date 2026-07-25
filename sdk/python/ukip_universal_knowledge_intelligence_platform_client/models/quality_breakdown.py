from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quality_breakdown_breakdown import QualityBreakdownBreakdown


T = TypeVar("T", bound="QualityBreakdown")


@_attrs_define
class QualityBreakdown:
    """
    Attributes:
        breakdown (QualityBreakdownBreakdown):
        entity_id (int):
        score (float):
        stored_score (float | None | Unset):
    """

    breakdown: QualityBreakdownBreakdown
    entity_id: int
    score: float
    stored_score: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        breakdown = self.breakdown.to_dict()

        entity_id = self.entity_id

        score = self.score

        stored_score: float | None | Unset
        if isinstance(self.stored_score, Unset):
            stored_score = UNSET
        else:
            stored_score = self.stored_score

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "breakdown": breakdown,
                "entity_id": entity_id,
                "score": score,
            }
        )
        if stored_score is not UNSET:
            field_dict["stored_score"] = stored_score

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quality_breakdown_breakdown import QualityBreakdownBreakdown

        d = dict(src_dict)
        breakdown = QualityBreakdownBreakdown.from_dict(d.pop("breakdown"))

        entity_id = d.pop("entity_id")

        score = d.pop("score")

        def _parse_stored_score(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stored_score = _parse_stored_score(d.pop("stored_score", UNSET))

        quality_breakdown = cls(
            breakdown=breakdown,
            entity_id=entity_id,
            score=score,
            stored_score=stored_score,
        )

        quality_breakdown.additional_properties = d
        return quality_breakdown

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
