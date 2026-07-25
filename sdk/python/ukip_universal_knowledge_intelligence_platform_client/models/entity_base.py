from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntityBase")


@_attrs_define
class EntityBase:
    """
    Attributes:
        canonical_id (None | str | Unset):
        domain (None | str | Unset):
        enrichment_citation_count (int | None | Unset):  Default: 0.
        enrichment_concepts (None | str | Unset):
        enrichment_doi (None | str | Unset):
        enrichment_source (None | str | Unset):
        enrichment_status (None | str | Unset):  Default: 'none'.
        enrichment_work_type (None | str | Unset):
        entity_type (None | str | Unset):
        primary_label (None | str | Unset):
        quality_score (float | None | Unset):
        secondary_label (None | str | Unset):
        validation_status (None | str | Unset):
    """

    canonical_id: None | str | Unset = UNSET
    domain: None | str | Unset = UNSET
    enrichment_citation_count: int | None | Unset = 0
    enrichment_concepts: None | str | Unset = UNSET
    enrichment_doi: None | str | Unset = UNSET
    enrichment_source: None | str | Unset = UNSET
    enrichment_status: None | str | Unset = "none"
    enrichment_work_type: None | str | Unset = UNSET
    entity_type: None | str | Unset = UNSET
    primary_label: None | str | Unset = UNSET
    quality_score: float | None | Unset = UNSET
    secondary_label: None | str | Unset = UNSET
    validation_status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        canonical_id: None | str | Unset
        if isinstance(self.canonical_id, Unset):
            canonical_id = UNSET
        else:
            canonical_id = self.canonical_id

        domain: None | str | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        enrichment_citation_count: int | None | Unset
        if isinstance(self.enrichment_citation_count, Unset):
            enrichment_citation_count = UNSET
        else:
            enrichment_citation_count = self.enrichment_citation_count

        enrichment_concepts: None | str | Unset
        if isinstance(self.enrichment_concepts, Unset):
            enrichment_concepts = UNSET
        else:
            enrichment_concepts = self.enrichment_concepts

        enrichment_doi: None | str | Unset
        if isinstance(self.enrichment_doi, Unset):
            enrichment_doi = UNSET
        else:
            enrichment_doi = self.enrichment_doi

        enrichment_source: None | str | Unset
        if isinstance(self.enrichment_source, Unset):
            enrichment_source = UNSET
        else:
            enrichment_source = self.enrichment_source

        enrichment_status: None | str | Unset
        if isinstance(self.enrichment_status, Unset):
            enrichment_status = UNSET
        else:
            enrichment_status = self.enrichment_status

        enrichment_work_type: None | str | Unset
        if isinstance(self.enrichment_work_type, Unset):
            enrichment_work_type = UNSET
        else:
            enrichment_work_type = self.enrichment_work_type

        entity_type: None | str | Unset
        if isinstance(self.entity_type, Unset):
            entity_type = UNSET
        else:
            entity_type = self.entity_type

        primary_label: None | str | Unset
        if isinstance(self.primary_label, Unset):
            primary_label = UNSET
        else:
            primary_label = self.primary_label

        quality_score: float | None | Unset
        if isinstance(self.quality_score, Unset):
            quality_score = UNSET
        else:
            quality_score = self.quality_score

        secondary_label: None | str | Unset
        if isinstance(self.secondary_label, Unset):
            secondary_label = UNSET
        else:
            secondary_label = self.secondary_label

        validation_status: None | str | Unset
        if isinstance(self.validation_status, Unset):
            validation_status = UNSET
        else:
            validation_status = self.validation_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if canonical_id is not UNSET:
            field_dict["canonical_id"] = canonical_id
        if domain is not UNSET:
            field_dict["domain"] = domain
        if enrichment_citation_count is not UNSET:
            field_dict["enrichment_citation_count"] = enrichment_citation_count
        if enrichment_concepts is not UNSET:
            field_dict["enrichment_concepts"] = enrichment_concepts
        if enrichment_doi is not UNSET:
            field_dict["enrichment_doi"] = enrichment_doi
        if enrichment_source is not UNSET:
            field_dict["enrichment_source"] = enrichment_source
        if enrichment_status is not UNSET:
            field_dict["enrichment_status"] = enrichment_status
        if enrichment_work_type is not UNSET:
            field_dict["enrichment_work_type"] = enrichment_work_type
        if entity_type is not UNSET:
            field_dict["entity_type"] = entity_type
        if primary_label is not UNSET:
            field_dict["primary_label"] = primary_label
        if quality_score is not UNSET:
            field_dict["quality_score"] = quality_score
        if secondary_label is not UNSET:
            field_dict["secondary_label"] = secondary_label
        if validation_status is not UNSET:
            field_dict["validation_status"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_canonical_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        canonical_id = _parse_canonical_id(d.pop("canonical_id", UNSET))

        def _parse_domain(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_enrichment_citation_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        enrichment_citation_count = _parse_enrichment_citation_count(d.pop("enrichment_citation_count", UNSET))

        def _parse_enrichment_concepts(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_concepts = _parse_enrichment_concepts(d.pop("enrichment_concepts", UNSET))

        def _parse_enrichment_doi(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_doi = _parse_enrichment_doi(d.pop("enrichment_doi", UNSET))

        def _parse_enrichment_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_source = _parse_enrichment_source(d.pop("enrichment_source", UNSET))

        def _parse_enrichment_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_status = _parse_enrichment_status(d.pop("enrichment_status", UNSET))

        def _parse_enrichment_work_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_work_type = _parse_enrichment_work_type(d.pop("enrichment_work_type", UNSET))

        def _parse_entity_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        entity_type = _parse_entity_type(d.pop("entity_type", UNSET))

        def _parse_primary_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_label = _parse_primary_label(d.pop("primary_label", UNSET))

        def _parse_quality_score(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        quality_score = _parse_quality_score(d.pop("quality_score", UNSET))

        def _parse_secondary_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        secondary_label = _parse_secondary_label(d.pop("secondary_label", UNSET))

        def _parse_validation_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        validation_status = _parse_validation_status(d.pop("validation_status", UNSET))

        entity_base = cls(
            canonical_id=canonical_id,
            domain=domain,
            enrichment_citation_count=enrichment_citation_count,
            enrichment_concepts=enrichment_concepts,
            enrichment_doi=enrichment_doi,
            enrichment_source=enrichment_source,
            enrichment_status=enrichment_status,
            enrichment_work_type=enrichment_work_type,
            entity_type=entity_type,
            primary_label=primary_label,
            quality_score=quality_score,
            secondary_label=secondary_label,
            validation_status=validation_status,
        )

        entity_base.additional_properties = d
        return entity_base

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
