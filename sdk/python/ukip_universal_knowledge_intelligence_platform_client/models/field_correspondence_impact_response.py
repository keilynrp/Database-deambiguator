from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_correspondence_impact_example import FieldCorrespondenceImpactExample


T = TypeVar("T", bound="FieldCorrespondenceImpactResponse")


@_attrs_define
class FieldCorrespondenceImpactResponse:
    """
    Attributes:
        affected_import_batches (int):
        affected_records (int):
        matching_suggestions (int):
        source_field (str):
        canonical_target (None | str | Unset):
        examples (list[FieldCorrespondenceImpactExample] | Unset):
        source_schema (None | str | Unset):
    """

    affected_import_batches: int
    affected_records: int
    matching_suggestions: int
    source_field: str
    canonical_target: None | str | Unset = UNSET
    examples: list[FieldCorrespondenceImpactExample] | Unset = UNSET
    source_schema: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        affected_import_batches = self.affected_import_batches

        affected_records = self.affected_records

        matching_suggestions = self.matching_suggestions

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

        source_schema: None | str | Unset
        if isinstance(self.source_schema, Unset):
            source_schema = UNSET
        else:
            source_schema = self.source_schema

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "affected_import_batches": affected_import_batches,
                "affected_records": affected_records,
                "matching_suggestions": matching_suggestions,
                "source_field": source_field,
            }
        )
        if canonical_target is not UNSET:
            field_dict["canonical_target"] = canonical_target
        if examples is not UNSET:
            field_dict["examples"] = examples
        if source_schema is not UNSET:
            field_dict["source_schema"] = source_schema

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_correspondence_impact_example import FieldCorrespondenceImpactExample

        d = dict(src_dict)
        affected_import_batches = d.pop("affected_import_batches")

        affected_records = d.pop("affected_records")

        matching_suggestions = d.pop("matching_suggestions")

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

        def _parse_source_schema(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_schema = _parse_source_schema(d.pop("source_schema", UNSET))

        field_correspondence_impact_response = cls(
            affected_import_batches=affected_import_batches,
            affected_records=affected_records,
            matching_suggestions=matching_suggestions,
            source_field=source_field,
            canonical_target=canonical_target,
            examples=examples,
            source_schema=source_schema,
        )

        field_correspondence_impact_response.additional_properties = d
        return field_correspondence_impact_response

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
