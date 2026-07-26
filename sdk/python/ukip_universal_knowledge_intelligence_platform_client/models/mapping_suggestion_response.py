from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MappingSuggestionResponse")


@_attrs_define
class MappingSuggestionResponse:
    """
    Attributes:
        canonical_target (str):
        confidence (float):
        evidence_samples (list[str]):
        id (int):
        rationale (str):
        source_field (str):
        status (str):
        evidence (list[str] | Unset):
        identifier_scheme (None | str | Unset):
        requires_review (bool | Unset):  Default: False.
        semantic_concept (None | str | Unset):
    """

    canonical_target: str
    confidence: float
    evidence_samples: list[str]
    id: int
    rationale: str
    source_field: str
    status: str
    evidence: list[str] | Unset = UNSET
    identifier_scheme: None | str | Unset = UNSET
    requires_review: bool | Unset = False
    semantic_concept: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        canonical_target = self.canonical_target

        confidence = self.confidence

        evidence_samples = self.evidence_samples

        id = self.id

        rationale = self.rationale

        source_field = self.source_field

        status = self.status

        evidence: list[str] | Unset = UNSET
        if not isinstance(self.evidence, Unset):
            evidence = self.evidence

        identifier_scheme: None | str | Unset
        if isinstance(self.identifier_scheme, Unset):
            identifier_scheme = UNSET
        else:
            identifier_scheme = self.identifier_scheme

        requires_review = self.requires_review

        semantic_concept: None | str | Unset
        if isinstance(self.semantic_concept, Unset):
            semantic_concept = UNSET
        else:
            semantic_concept = self.semantic_concept

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "canonical_target": canonical_target,
                "confidence": confidence,
                "evidence_samples": evidence_samples,
                "id": id,
                "rationale": rationale,
                "source_field": source_field,
                "status": status,
            }
        )
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if identifier_scheme is not UNSET:
            field_dict["identifier_scheme"] = identifier_scheme
        if requires_review is not UNSET:
            field_dict["requires_review"] = requires_review
        if semantic_concept is not UNSET:
            field_dict["semantic_concept"] = semantic_concept

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        canonical_target = d.pop("canonical_target")

        confidence = d.pop("confidence")

        evidence_samples = cast(list[str], d.pop("evidence_samples"))

        id = d.pop("id")

        rationale = d.pop("rationale")

        source_field = d.pop("source_field")

        status = d.pop("status")

        evidence = cast(list[str], d.pop("evidence", UNSET))

        def _parse_identifier_scheme(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        identifier_scheme = _parse_identifier_scheme(d.pop("identifier_scheme", UNSET))

        requires_review = d.pop("requires_review", UNSET)

        def _parse_semantic_concept(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        semantic_concept = _parse_semantic_concept(d.pop("semantic_concept", UNSET))

        mapping_suggestion_response = cls(
            canonical_target=canonical_target,
            confidence=confidence,
            evidence_samples=evidence_samples,
            id=id,
            rationale=rationale,
            source_field=source_field,
            status=status,
            evidence=evidence,
            identifier_scheme=identifier_scheme,
            requires_review=requires_review,
            semantic_concept=semantic_concept,
        )

        mapping_suggestion_response.additional_properties = d
        return mapping_suggestion_response

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
