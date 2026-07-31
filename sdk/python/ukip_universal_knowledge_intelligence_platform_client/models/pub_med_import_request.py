from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PubMedImportRequest")


@_attrs_define
class PubMedImportRequest:
    """
    Attributes:
        domain (str): Registered domain the imported records are filed under. Required: this is written once at ingest
            and cannot be changed afterwards.
        query (str):
        limit (int | Unset):  Default: 100.
        preview (bool | Unset):  Default: False.
    """

    domain: str
    query: str
    limit: int | Unset = 100
    preview: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain = self.domain

        query = self.query

        limit = self.limit

        preview = self.preview

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain": domain,
                "query": query,
            }
        )
        if limit is not UNSET:
            field_dict["limit"] = limit
        if preview is not UNSET:
            field_dict["preview"] = preview

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domain = d.pop("domain")

        query = d.pop("query")

        limit = d.pop("limit", UNSET)

        preview = d.pop("preview", UNSET)

        pub_med_import_request = cls(
            domain=domain,
            query=query,
            limit=limit,
            preview=preview,
        )

        pub_med_import_request.additional_properties = d
        return pub_med_import_request

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
