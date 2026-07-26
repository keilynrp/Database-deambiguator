from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_correspondence_impact_example import FieldCorrespondenceImpactExample


T = TypeVar("T", bound="FieldCorrespondenceApplyResponse")


@_attrs_define
class FieldCorrespondenceApplyResponse:
    """
    Attributes:
        affected_import_batches (int):
        affected_records (int):
        dry_run (bool):
        matching_suggestions (int):
        overwrite_existing (bool):
        source_field (str):
        canonical_target (None | str | Unset):
        examples (list[FieldCorrespondenceImpactExample] | Unset):
        job_id (int | None | Unset):
        skipped_existing (int | Unset):  Default: 0.
        skipped_missing_value (int | Unset):  Default: 0.
        source_schema (None | str | Unset):
        updated_records (int | Unset):  Default: 0.
    """

    affected_import_batches: int
    affected_records: int
    dry_run: bool
    matching_suggestions: int
    overwrite_existing: bool
    source_field: str
    canonical_target: None | str | Unset = UNSET
    examples: list[FieldCorrespondenceImpactExample] | Unset = UNSET
    job_id: int | None | Unset = UNSET
    skipped_existing: int | Unset = 0
    skipped_missing_value: int | Unset = 0
    source_schema: None | str | Unset = UNSET
    updated_records: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        affected_import_batches = self.affected_import_batches

        affected_records = self.affected_records

        dry_run = self.dry_run

        matching_suggestions = self.matching_suggestions

        overwrite_existing = self.overwrite_existing

        source_field = self.source_field

        canonical_target: None | str | Unset
        if isinstance(self.canonical_target, Unset):
            canonical_target = UNSET
        else:
            canonical_target = self.canonical_target

        examples: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.examples, Unset):
            examples = []
            for examples_item_data in self.examples:
                examples_item = examples_item_data.to_dict()
                examples.append(examples_item)

        job_id: int | None | Unset
        if isinstance(self.job_id, Unset):
            job_id = UNSET
        else:
            job_id = self.job_id

        skipped_existing = self.skipped_existing

        skipped_missing_value = self.skipped_missing_value

        source_schema: None | str | Unset
        if isinstance(self.source_schema, Unset):
            source_schema = UNSET
        else:
            source_schema = self.source_schema

        updated_records = self.updated_records

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "affected_import_batches": affected_import_batches,
                "affected_records": affected_records,
                "dry_run": dry_run,
                "matching_suggestions": matching_suggestions,
                "overwrite_existing": overwrite_existing,
                "source_field": source_field,
            }
        )
        if canonical_target is not UNSET:
            field_dict["canonical_target"] = canonical_target
        if examples is not UNSET:
            field_dict["examples"] = examples
        if job_id is not UNSET:
            field_dict["job_id"] = job_id
        if skipped_existing is not UNSET:
            field_dict["skipped_existing"] = skipped_existing
        if skipped_missing_value is not UNSET:
            field_dict["skipped_missing_value"] = skipped_missing_value
        if source_schema is not UNSET:
            field_dict["source_schema"] = source_schema
        if updated_records is not UNSET:
            field_dict["updated_records"] = updated_records

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_correspondence_impact_example import FieldCorrespondenceImpactExample

        d = dict(src_dict)
        affected_import_batches = d.pop("affected_import_batches")

        affected_records = d.pop("affected_records")

        dry_run = d.pop("dry_run")

        matching_suggestions = d.pop("matching_suggestions")

        overwrite_existing = d.pop("overwrite_existing")

        source_field = d.pop("source_field")

        def _parse_canonical_target(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        canonical_target = _parse_canonical_target(d.pop("canonical_target", UNSET))

        _examples = d.pop("examples", UNSET)
        examples: list[FieldCorrespondenceImpactExample] | Unset = UNSET
        if _examples is not UNSET:
            examples = []
            for examples_item_data in _examples:
                examples_item = FieldCorrespondenceImpactExample.from_dict(examples_item_data)

                examples.append(examples_item)

        def _parse_job_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        job_id = _parse_job_id(d.pop("job_id", UNSET))

        skipped_existing = d.pop("skipped_existing", UNSET)

        skipped_missing_value = d.pop("skipped_missing_value", UNSET)

        def _parse_source_schema(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_schema = _parse_source_schema(d.pop("source_schema", UNSET))

        updated_records = d.pop("updated_records", UNSET)

        field_correspondence_apply_response = cls(
            affected_import_batches=affected_import_batches,
            affected_records=affected_records,
            dry_run=dry_run,
            matching_suggestions=matching_suggestions,
            overwrite_existing=overwrite_existing,
            source_field=source_field,
            canonical_target=canonical_target,
            examples=examples,
            job_id=job_id,
            skipped_existing=skipped_existing,
            skipped_missing_value=skipped_missing_value,
            source_schema=source_schema,
            updated_records=updated_records,
        )

        field_correspondence_apply_response.additional_properties = d
        return field_correspondence_apply_response

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
