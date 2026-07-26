from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authority_entity_type import AuthorityEntityType
from ..types import UNSET, Unset

T = TypeVar("T", bound="AuthorityResolveRequest")


@_attrs_define
class AuthorityResolveRequest:
    """
    Attributes:
        field_name (str):
        value (str):
        context_affiliation (None | str | Unset):
        context_doi (None | str | Unset):
        context_orcid_hint (None | str | Unset):
        context_year (int | None | Unset):
        entity_type (AuthorityEntityType | Unset):
    """

    field_name: str
    value: str
    context_affiliation: None | str | Unset = UNSET
    context_doi: None | str | Unset = UNSET
    context_orcid_hint: None | str | Unset = UNSET
    context_year: int | None | Unset = UNSET
    entity_type: AuthorityEntityType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_name = self.field_name

        value = self.value

        context_affiliation: None | str | Unset
        if isinstance(self.context_affiliation, Unset):
            context_affiliation = UNSET
        else:
            context_affiliation = self.context_affiliation

        context_doi: None | str | Unset
        if isinstance(self.context_doi, Unset):
            context_doi = UNSET
        else:
            context_doi = self.context_doi

        context_orcid_hint: None | str | Unset
        if isinstance(self.context_orcid_hint, Unset):
            context_orcid_hint = UNSET
        else:
            context_orcid_hint = self.context_orcid_hint

        context_year: int | None | Unset
        if isinstance(self.context_year, Unset):
            context_year = UNSET
        else:
            context_year = self.context_year

        entity_type: str | Unset = UNSET
        if not isinstance(self.entity_type, Unset):
            entity_type = self.entity_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field_name": field_name,
                "value": value,
            }
        )
        if context_affiliation is not UNSET:
            field_dict["context_affiliation"] = context_affiliation
        if context_doi is not UNSET:
            field_dict["context_doi"] = context_doi
        if context_orcid_hint is not UNSET:
            field_dict["context_orcid_hint"] = context_orcid_hint
        if context_year is not UNSET:
            field_dict["context_year"] = context_year
        if entity_type is not UNSET:
            field_dict["entity_type"] = entity_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field_name = d.pop("field_name")

        value = d.pop("value")

        def _parse_context_affiliation(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        context_affiliation = _parse_context_affiliation(d.pop("context_affiliation", UNSET))

        def _parse_context_doi(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        context_doi = _parse_context_doi(d.pop("context_doi", UNSET))

        def _parse_context_orcid_hint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        context_orcid_hint = _parse_context_orcid_hint(d.pop("context_orcid_hint", UNSET))

        def _parse_context_year(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        context_year = _parse_context_year(d.pop("context_year", UNSET))

        _entity_type = d.pop("entity_type", UNSET)
        entity_type: AuthorityEntityType | Unset
        if isinstance(_entity_type, Unset):
            entity_type = UNSET
        else:
            entity_type = AuthorityEntityType(_entity_type)

        authority_resolve_request = cls(
            field_name=field_name,
            value=value,
            context_affiliation=context_affiliation,
            context_doi=context_doi,
            context_orcid_hint=context_orcid_hint,
            context_year=context_year,
            entity_type=entity_type,
        )

        authority_resolve_request.additional_properties = d
        return authority_resolve_request

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
