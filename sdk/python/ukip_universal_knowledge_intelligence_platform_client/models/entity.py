from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Entity")


@_attrs_define
class Entity:
    """
    Attributes:
        id (int):
        attributes_json (None | str | Unset):
        canonical_id (None | str | Unset):
        domain (None | str | Unset):
        enrichment_citation_count (int | None | Unset):  Default: 0.
        enrichment_concepts (None | str | Unset):
        enrichment_doi (None | str | Unset):
        enrichment_issn_l (None | str | Unset):
        enrichment_source (None | str | Unset):
        enrichment_status (None | str | Unset):  Default: 'none'.
        enrichment_work_type (None | str | Unset):
        entity_type (None | str | Unset):
        import_batch_id (int | None | Unset):
        journal_display_name (None | str | Unset):
        journal_nif (float | None | Unset):
        journal_nif_bayes (float | None | Unset):
        journal_nif_bayes_ready (bool | Unset):  Default: False.
        journal_nif_ci_high (float | None | Unset):
        journal_nif_ci_low (float | None | Unset):
        normalized_json (None | str | Unset):
        primary_label (None | str | Unset):
        quality_score (float | None | Unset):
        secondary_label (None | str | Unset):
        source (None | str | Unset):
        validation_status (None | str | Unset):
    """

    id: int
    attributes_json: None | str | Unset = UNSET
    canonical_id: None | str | Unset = UNSET
    domain: None | str | Unset = UNSET
    enrichment_citation_count: int | None | Unset = 0
    enrichment_concepts: None | str | Unset = UNSET
    enrichment_doi: None | str | Unset = UNSET
    enrichment_issn_l: None | str | Unset = UNSET
    enrichment_source: None | str | Unset = UNSET
    enrichment_status: None | str | Unset = "none"
    enrichment_work_type: None | str | Unset = UNSET
    entity_type: None | str | Unset = UNSET
    import_batch_id: int | None | Unset = UNSET
    journal_display_name: None | str | Unset = UNSET
    journal_nif: float | None | Unset = UNSET
    journal_nif_bayes: float | None | Unset = UNSET
    journal_nif_bayes_ready: bool | Unset = False
    journal_nif_ci_high: float | None | Unset = UNSET
    journal_nif_ci_low: float | None | Unset = UNSET
    normalized_json: None | str | Unset = UNSET
    primary_label: None | str | Unset = UNSET
    quality_score: float | None | Unset = UNSET
    secondary_label: None | str | Unset = UNSET
    source: None | str | Unset = UNSET
    validation_status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        attributes_json: None | str | Unset
        if isinstance(self.attributes_json, Unset):
            attributes_json = UNSET
        else:
            attributes_json = self.attributes_json

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

        enrichment_issn_l: None | str | Unset
        if isinstance(self.enrichment_issn_l, Unset):
            enrichment_issn_l = UNSET
        else:
            enrichment_issn_l = self.enrichment_issn_l

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

        import_batch_id: int | None | Unset
        if isinstance(self.import_batch_id, Unset):
            import_batch_id = UNSET
        else:
            import_batch_id = self.import_batch_id

        journal_display_name: None | str | Unset
        if isinstance(self.journal_display_name, Unset):
            journal_display_name = UNSET
        else:
            journal_display_name = self.journal_display_name

        journal_nif: float | None | Unset
        if isinstance(self.journal_nif, Unset):
            journal_nif = UNSET
        else:
            journal_nif = self.journal_nif

        journal_nif_bayes: float | None | Unset
        if isinstance(self.journal_nif_bayes, Unset):
            journal_nif_bayes = UNSET
        else:
            journal_nif_bayes = self.journal_nif_bayes

        journal_nif_bayes_ready = self.journal_nif_bayes_ready

        journal_nif_ci_high: float | None | Unset
        if isinstance(self.journal_nif_ci_high, Unset):
            journal_nif_ci_high = UNSET
        else:
            journal_nif_ci_high = self.journal_nif_ci_high

        journal_nif_ci_low: float | None | Unset
        if isinstance(self.journal_nif_ci_low, Unset):
            journal_nif_ci_low = UNSET
        else:
            journal_nif_ci_low = self.journal_nif_ci_low

        normalized_json: None | str | Unset
        if isinstance(self.normalized_json, Unset):
            normalized_json = UNSET
        else:
            normalized_json = self.normalized_json

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

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        validation_status: None | str | Unset
        if isinstance(self.validation_status, Unset):
            validation_status = UNSET
        else:
            validation_status = self.validation_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if attributes_json is not UNSET:
            field_dict["attributes_json"] = attributes_json
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
        if enrichment_issn_l is not UNSET:
            field_dict["enrichment_issn_l"] = enrichment_issn_l
        if enrichment_source is not UNSET:
            field_dict["enrichment_source"] = enrichment_source
        if enrichment_status is not UNSET:
            field_dict["enrichment_status"] = enrichment_status
        if enrichment_work_type is not UNSET:
            field_dict["enrichment_work_type"] = enrichment_work_type
        if entity_type is not UNSET:
            field_dict["entity_type"] = entity_type
        if import_batch_id is not UNSET:
            field_dict["import_batch_id"] = import_batch_id
        if journal_display_name is not UNSET:
            field_dict["journal_display_name"] = journal_display_name
        if journal_nif is not UNSET:
            field_dict["journal_nif"] = journal_nif
        if journal_nif_bayes is not UNSET:
            field_dict["journal_nif_bayes"] = journal_nif_bayes
        if journal_nif_bayes_ready is not UNSET:
            field_dict["journal_nif_bayes_ready"] = journal_nif_bayes_ready
        if journal_nif_ci_high is not UNSET:
            field_dict["journal_nif_ci_high"] = journal_nif_ci_high
        if journal_nif_ci_low is not UNSET:
            field_dict["journal_nif_ci_low"] = journal_nif_ci_low
        if normalized_json is not UNSET:
            field_dict["normalized_json"] = normalized_json
        if primary_label is not UNSET:
            field_dict["primary_label"] = primary_label
        if quality_score is not UNSET:
            field_dict["quality_score"] = quality_score
        if secondary_label is not UNSET:
            field_dict["secondary_label"] = secondary_label
        if source is not UNSET:
            field_dict["source"] = source
        if validation_status is not UNSET:
            field_dict["validation_status"] = validation_status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        def _parse_attributes_json(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        attributes_json = _parse_attributes_json(d.pop("attributes_json", UNSET))

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

        def _parse_enrichment_issn_l(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        enrichment_issn_l = _parse_enrichment_issn_l(d.pop("enrichment_issn_l", UNSET))

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

        def _parse_import_batch_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        import_batch_id = _parse_import_batch_id(d.pop("import_batch_id", UNSET))

        def _parse_journal_display_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        journal_display_name = _parse_journal_display_name(d.pop("journal_display_name", UNSET))

        def _parse_journal_nif(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        journal_nif = _parse_journal_nif(d.pop("journal_nif", UNSET))

        def _parse_journal_nif_bayes(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        journal_nif_bayes = _parse_journal_nif_bayes(d.pop("journal_nif_bayes", UNSET))

        journal_nif_bayes_ready = d.pop("journal_nif_bayes_ready", UNSET)

        def _parse_journal_nif_ci_high(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        journal_nif_ci_high = _parse_journal_nif_ci_high(d.pop("journal_nif_ci_high", UNSET))

        def _parse_journal_nif_ci_low(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        journal_nif_ci_low = _parse_journal_nif_ci_low(d.pop("journal_nif_ci_low", UNSET))

        def _parse_normalized_json(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        normalized_json = _parse_normalized_json(d.pop("normalized_json", UNSET))

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

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        def _parse_validation_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        validation_status = _parse_validation_status(d.pop("validation_status", UNSET))

        entity = cls(
            id=id,
            attributes_json=attributes_json,
            canonical_id=canonical_id,
            domain=domain,
            enrichment_citation_count=enrichment_citation_count,
            enrichment_concepts=enrichment_concepts,
            enrichment_doi=enrichment_doi,
            enrichment_issn_l=enrichment_issn_l,
            enrichment_source=enrichment_source,
            enrichment_status=enrichment_status,
            enrichment_work_type=enrichment_work_type,
            entity_type=entity_type,
            import_batch_id=import_batch_id,
            journal_display_name=journal_display_name,
            journal_nif=journal_nif,
            journal_nif_bayes=journal_nif_bayes,
            journal_nif_bayes_ready=journal_nif_bayes_ready,
            journal_nif_ci_high=journal_nif_ci_high,
            journal_nif_ci_low=journal_nif_ci_low,
            normalized_json=normalized_json,
            primary_label=primary_label,
            quality_score=quality_score,
            secondary_label=secondary_label,
            source=source,
            validation_status=validation_status,
        )

        entity.additional_properties = d
        return entity

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
