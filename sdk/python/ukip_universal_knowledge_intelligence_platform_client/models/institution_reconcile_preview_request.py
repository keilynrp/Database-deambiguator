from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="InstitutionReconcilePreviewRequest")


@_attrs_define
class InstitutionReconcilePreviewRequest:
    """
    Attributes:
        domain_id (None | str | Unset):
        entity_ids (list[int] | None | Unset):
        limit (int | Unset):  Default: 25.
        live_lookup (bool | Unset):  Default: False.
    """

    domain_id: None | str | Unset = UNSET
    entity_ids: list[int] | None | Unset = UNSET
    limit: int | Unset = 25
    live_lookup: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        else:
            domain_id = self.domain_id

        entity_ids: list[int] | None | Unset
        if isinstance(self.entity_ids, Unset):
            entity_ids = UNSET
        elif isinstance(self.entity_ids, list):
            entity_ids = self.entity_ids

        else:
            entity_ids = self.entity_ids

        limit = self.limit

        live_lookup = self.live_lookup

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if entity_ids is not UNSET:
            field_dict["entity_ids"] = entity_ids
        if limit is not UNSET:
            field_dict["limit"] = limit
        if live_lookup is not UNSET:
            field_dict["live_lookup"] = live_lookup

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_domain_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        def _parse_entity_ids(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                entity_ids_type_0 = cast(list[int], data)

                return entity_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        entity_ids = _parse_entity_ids(d.pop("entity_ids", UNSET))

        limit = d.pop("limit", UNSET)

        live_lookup = d.pop("live_lookup", UNSET)

        institution_reconcile_preview_request = cls(
            domain_id=domain_id,
            entity_ids=entity_ids,
            limit=limit,
            live_lookup=live_lookup,
        )

        institution_reconcile_preview_request.additional_properties = d
        return institution_reconcile_preview_request

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
