from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceRuleResponse")


@_attrs_define
class FieldCorrespondenceRuleResponse:
    """
    Attributes:
        confidence (float):
        id (int):
        is_active (bool):
        source_field (str):
        canonical_target (None | str | Unset):
        created_at (None | str | Unset):
        created_by_id (int | None | Unset):
        created_from_suggestion_id (int | None | Unset):
        evidence (list[str] | Unset):
        identifier_scheme (None | str | Unset):
        review_status (str | Unset):  Default: 'pending'.
        semantic_concept (None | str | Unset):
        source_schema (None | str | Unset):
        updated_at (None | str | Unset):
    """

    confidence: float
    id: int
    is_active: bool
    source_field: str
    canonical_target: None | str | Unset = UNSET
    created_at: None | str | Unset = UNSET
    created_by_id: int | None | Unset = UNSET
    created_from_suggestion_id: int | None | Unset = UNSET
    evidence: list[str] | Unset = UNSET
    identifier_scheme: None | str | Unset = UNSET
    review_status: str | Unset = "pending"
    semantic_concept: None | str | Unset = UNSET
    source_schema: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        confidence = self.confidence

        id = self.id

        is_active = self.is_active

        source_field = self.source_field

        canonical_target: None | str | Unset
        if isinstance(self.canonical_target, Unset):
            canonical_target = UNSET
        else:
            canonical_target = self.canonical_target

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        created_by_id: int | None | Unset
        if isinstance(self.created_by_id, Unset):
            created_by_id = UNSET
        else:
            created_by_id = self.created_by_id

        created_from_suggestion_id: int | None | Unset
        if isinstance(self.created_from_suggestion_id, Unset):
            created_from_suggestion_id = UNSET
        else:
            created_from_suggestion_id = self.created_from_suggestion_id

        evidence: list[str] | Unset = UNSET
        if not isinstance(self.evidence, Unset):
            evidence = self.evidence

        identifier_scheme: None | str | Unset
        if isinstance(self.identifier_scheme, Unset):
            identifier_scheme = UNSET
        else:
            identifier_scheme = self.identifier_scheme

        review_status = self.review_status

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

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "confidence": confidence,
                "id": id,
                "is_active": is_active,
                "source_field": source_field,
            }
        )
        if canonical_target is not UNSET:
            field_dict["canonical_target"] = canonical_target
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by_id is not UNSET:
            field_dict["created_by_id"] = created_by_id
        if created_from_suggestion_id is not UNSET:
            field_dict["created_from_suggestion_id"] = created_from_suggestion_id
        if evidence is not UNSET:
            field_dict["evidence"] = evidence
        if identifier_scheme is not UNSET:
            field_dict["identifier_scheme"] = identifier_scheme
        if review_status is not UNSET:
            field_dict["review_status"] = review_status
        if semantic_concept is not UNSET:
            field_dict["semantic_concept"] = semantic_concept
        if source_schema is not UNSET:
            field_dict["source_schema"] = source_schema
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        confidence = d.pop("confidence")

        id = d.pop("id")

        is_active = d.pop("is_active")

        source_field = d.pop("source_field")

        def _parse_canonical_target(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        canonical_target = _parse_canonical_target(d.pop("canonical_target", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_created_by_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        created_by_id = _parse_created_by_id(d.pop("created_by_id", UNSET))

        def _parse_created_from_suggestion_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        created_from_suggestion_id = _parse_created_from_suggestion_id(d.pop("created_from_suggestion_id", UNSET))

        evidence = cast(list[str], d.pop("evidence", UNSET))

        def _parse_identifier_scheme(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        identifier_scheme = _parse_identifier_scheme(d.pop("identifier_scheme", UNSET))

        review_status = d.pop("review_status", UNSET)

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

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        field_correspondence_rule_response = cls(
            confidence=confidence,
            id=id,
            is_active=is_active,
            source_field=source_field,
            canonical_target=canonical_target,
            created_at=created_at,
            created_by_id=created_by_id,
            created_from_suggestion_id=created_from_suggestion_id,
            evidence=evidence,
            identifier_scheme=identifier_scheme,
            review_status=review_status,
            semantic_concept=semantic_concept,
            source_schema=source_schema,
            updated_at=updated_at,
        )

        field_correspondence_rule_response.additional_properties = d
        return field_correspondence_rule_response

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
