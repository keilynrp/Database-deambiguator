from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceRulePayload")


@_attrs_define
class FieldCorrespondenceRulePayload:
    """
    Attributes:
        source_field (str):
        canonical_target (None | str | Unset):
        confidence (float | Unset):  Default: 1.0.
        evidence (list[str] | Unset):
        identifier_scheme (None | str | Unset):
        semantic_concept (None | str | Unset):
        source_schema (None | str | Unset):
    """

    source_field: str
    canonical_target: None | str | Unset = UNSET
    confidence: float | Unset = 1.0
    evidence: list[str] | Unset = UNSET
    identifier_scheme: None | str | Unset = UNSET
    semantic_concept: None | str | Unset = UNSET
    source_schema: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_field = self.source_field

        canonical_target: None | str | Unset
        if isinstance(self.canonical_target, Unset):
            canonical_target = UNSET
        else:
            canonical_target = self.canonical_target

        confidence = self.confidence

        evidence: list[str] | Unset = UNSET
        if not isinstance(self.evidence, Unset):
            evidence = self.evidence

        identifier_scheme: None | str | Unset
        if isinstance(self.identifier_scheme, Unset):
            identifier_scheme = UNSET
        else:
            identifier_scheme = self.identifier_scheme

        semantic_concept: None | str | Unset
        if isinstance(self.semantic_concept, Unset):
            semantic_concept = UNSET
        else:
            semantic_concept = self.semantic_concept

        source_schema: None | str | Unset
        if isinstance(self.source_schema, Unset):
            source_schema = UNSET
        else:
            source_schema = self.source_schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_field": source_field,
            }
        )
        if canonical_target is not UNSET:
            field_dict["canonical_target"] = canonical_target
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if identifier_scheme is not UNSET:
            field_dict["identifier_scheme"] = identifier_scheme
        if semantic_concept is not UNSET:
            field_dict["semantic_concept"] = semantic_concept
        if source_schema is not UNSET:
            field_dict["source_schema"] = source_schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_field = d.pop("source_field")

        def _parse_canonical_target(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        canonical_target = _parse_canonical_target(d.pop("canonical_target", UNSET))

        confidence = d.pop("confidence", UNSET)

        evidence = cast(list[str], d.pop("evidence", UNSET))

        def _parse_identifier_scheme(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        identifier_scheme = _parse_identifier_scheme(d.pop("identifier_scheme", UNSET))

        def _parse_semantic_concept(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        semantic_concept = _parse_semantic_concept(d.pop("semantic_concept", UNSET))

        def _parse_source_schema(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_schema = _parse_source_schema(d.pop("source_schema", UNSET))

        field_correspondence_rule_payload = cls(
            source_field=source_field,
            canonical_target=canonical_target,
            confidence=confidence,
            evidence=evidence,
            identifier_scheme=identifier_scheme,
            semantic_concept=semantic_concept,
            source_schema=source_schema,
        )

        field_correspondence_rule_payload.additional_properties = d
        return field_correspondence_rule_payload

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
