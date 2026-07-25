from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySnap")


@_attrs_define
class EntitySnap:
    """
    Attributes:
        enrichment_status (str):
        id (int):
        validation_status (str):
        canonical_id (None | str | Unset):
        entity_type (None | str | Unset):
        primary_label (None | str | Unset):
        secondary_label (None | str | Unset):
    """

    enrichment_status: str
    id: int
    validation_status: str
    canonical_id: None | str | Unset = UNSET
    entity_type: None | str | Unset = UNSET
    primary_label: None | str | Unset = UNSET
    secondary_label: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enrichment_status = self.enrichment_status

        id = self.id

        validation_status = self.validation_status

        canonical_id: None | str | Unset
        if isinstance(self.canonical_id, Unset):
            canonical_id = UNSET
        else:
            canonical_id = self.canonical_id

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

        secondary_label: None | str | Unset
        if isinstance(self.secondary_label, Unset):
            secondary_label = UNSET
        else:
            secondary_label = self.secondary_label

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enrichment_status": enrichment_status,
                "id": id,
                "validation_status": validation_status,
            }
        )
        if canonical_id is not UNSET:
            field_dict["canonical_id"] = canonical_id
        if entity_type is not UNSET:
            field_dict["entity_type"] = entity_type
        if primary_label is not UNSET:
            field_dict["primary_label"] = primary_label
        if secondary_label is not UNSET:
            field_dict["secondary_label"] = secondary_label

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enrichment_status = d.pop("enrichment_status")

        id = d.pop("id")

        validation_status = d.pop("validation_status")

        def _parse_canonical_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        canonical_id = _parse_canonical_id(d.pop("canonical_id", UNSET))

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

        def _parse_secondary_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        secondary_label = _parse_secondary_label(d.pop("secondary_label", UNSET))

        entity_snap = cls(
            enrichment_status=enrichment_status,
            id=id,
            validation_status=validation_status,
            canonical_id=canonical_id,
            entity_type=entity_type,
            primary_label=primary_label,
            secondary_label=secondary_label,
        )

        entity_snap.additional_properties = d
        return entity_snap

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
