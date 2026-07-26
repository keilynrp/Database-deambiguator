from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authority_entity_type import AuthorityEntityType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchResolveRequest")


@_attrs_define
class BatchResolveRequest:
    """
    Attributes:
        field_name (str):
        entity_type (AuthorityEntityType | Unset):
        limit (int | Unset):  Default: 20.
        skip_existing (bool | Unset):  Default: True.
        value_source (None | str | Unset):
    """

    field_name: str
    entity_type: AuthorityEntityType | Unset = UNSET
    limit: int | Unset = 20
    skip_existing: bool | Unset = True
    value_source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_name = self.field_name

        entity_type: str | Unset = UNSET
        if not isinstance(self.entity_type, Unset):
            entity_type = self.entity_type.value

        limit = self.limit

        skip_existing = self.skip_existing

        value_source: None | str | Unset
        if isinstance(self.value_source, Unset):
            value_source = UNSET
        else:
            value_source = self.value_source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field_name": field_name,
            }
        )
        if entity_type is not UNSET:
            field_dict["entity_type"] = entity_type
        if limit is not UNSET:
            field_dict["limit"] = limit
        if skip_existing is not UNSET:
            field_dict["skip_existing"] = skip_existing
        if value_source is not UNSET:
            field_dict["value_source"] = value_source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_name = d.pop("field_name")

        _entity_type = d.pop("entity_type", UNSET)
        entity_type: AuthorityEntityType | Unset
        if isinstance(_entity_type, Unset):
            entity_type = UNSET
        else:
            entity_type = AuthorityEntityType(_entity_type)

        limit = d.pop("limit", UNSET)

        skip_existing = d.pop("skip_existing", UNSET)

        def _parse_value_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        value_source = _parse_value_source(d.pop("value_source", UNSET))

        batch_resolve_request = cls(
            field_name=field_name,
            entity_type=entity_type,
            limit=limit,
            skip_existing=skip_existing,
            value_source=value_source,
        )

        batch_resolve_request.additional_properties = d
        return batch_resolve_request

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
