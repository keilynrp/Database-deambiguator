from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FieldCorrespondenceImpactExample")


@_attrs_define
class FieldCorrespondenceImpactExample:
    """
    Attributes:
        entity_id (int):
        location (str):
        source_field (str):
        current_value (None | str | Unset):
        import_batch_id (int | None | Unset):
        primary_label (None | str | Unset):
    """

    entity_id: int
    location: str
    source_field: str
    current_value: None | str | Unset = UNSET
    import_batch_id: int | None | Unset = UNSET
    primary_label: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        entity_id = self.entity_id

        location = self.location

        source_field = self.source_field

        current_value: None | str | Unset
        if isinstance(self.current_value, Unset):
            current_value = UNSET
        else:
            current_value = self.current_value

        import_batch_id: int | None | Unset
        if isinstance(self.import_batch_id, Unset):
            import_batch_id = UNSET
        else:
            import_batch_id = self.import_batch_id

        primary_label: None | str | Unset
        if isinstance(self.primary_label, Unset):
            primary_label = UNSET
        else:
            primary_label = self.primary_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "entity_id": entity_id,
                "location": location,
                "source_field": source_field,
            }
        )
        if current_value is not UNSET:
            field_dict["current_value"] = current_value
        if import_batch_id is not UNSET:
            field_dict["import_batch_id"] = import_batch_id
        if primary_label is not UNSET:
            field_dict["primary_label"] = primary_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        entity_id = d.pop("entity_id")

        location = d.pop("location")

        source_field = d.pop("source_field")

        def _parse_current_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        current_value = _parse_current_value(d.pop("current_value", UNSET))

        def _parse_import_batch_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        import_batch_id = _parse_import_batch_id(d.pop("import_batch_id", UNSET))

        def _parse_primary_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        primary_label = _parse_primary_label(d.pop("primary_label", UNSET))

        field_correspondence_impact_example = cls(
            entity_id=entity_id,
            location=location,
            source_field=source_field,
            current_value=current_value,
            import_batch_id=import_batch_id,
            primary_label=primary_label,
        )

        field_correspondence_impact_example.additional_properties = d
        return field_correspondence_impact_example

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
