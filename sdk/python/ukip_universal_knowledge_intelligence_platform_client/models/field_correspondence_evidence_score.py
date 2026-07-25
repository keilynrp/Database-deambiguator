from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceEvidenceScore")


@_attrs_define
class FieldCorrespondenceEvidenceScore:
    """
    Attributes:
        affected_records (int):
        matching_suggestions (int):
        rule_id (int):
        score (str):
        validation_status (str):
        collision_count (int | Unset):  Default: 0.
        sample_values (list[str] | Unset):
    """

    affected_records: int
    matching_suggestions: int
    rule_id: int
    score: str
    validation_status: str
    collision_count: int | Unset = 0
    sample_values: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        affected_records = self.affected_records

        matching_suggestions = self.matching_suggestions

        rule_id = self.rule_id

        score = self.score

        validation_status = self.validation_status

        collision_count = self.collision_count

        sample_values: list[str] | Unset = UNSET
        if not isinstance(self.sample_values, Unset):
            sample_values = self.sample_values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "affected_records": affected_records,
                "matching_suggestions": matching_suggestions,
                "rule_id": rule_id,
                "score": score,
                "validation_status": validation_status,
            }
        )
        if collision_count is not UNSET:
            field_dict["collision_count"] = collision_count
        if sample_values is not UNSET:
            field_dict["sample_values"] = sample_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        affected_records = d.pop("affected_records")

        matching_suggestions = d.pop("matching_suggestions")

        rule_id = d.pop("rule_id")

        score = d.pop("score")

        validation_status = d.pop("validation_status")

        collision_count = d.pop("collision_count", UNSET)

        sample_values = cast(list[str], d.pop("sample_values", UNSET))

        field_correspondence_evidence_score = cls(
            affected_records=affected_records,
            matching_suggestions=matching_suggestions,
            rule_id=rule_id,
            score=score,
            validation_status=validation_status,
            collision_count=collision_count,
            sample_values=sample_values,
        )

        field_correspondence_evidence_score.additional_properties = d
        return field_correspondence_evidence_score

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
