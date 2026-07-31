from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.open_alex_import_request_filters_type_0 import OpenAlexImportRequestFiltersType0


T = TypeVar("T", bound="OpenAlexImportRequest")


@_attrs_define
class OpenAlexImportRequest:
    """
    Attributes:
        domain (str): Registered domain the imported records are filed under. Required: this is written once at ingest
            and cannot be changed afterwards.
        query (str):
        filters (None | OpenAlexImportRequestFiltersType0 | Unset):
        limit (int | Unset):  Default: 100.
        preview (bool | Unset):  Default: False.
    """

    domain: str
    query: str
    filters: None | OpenAlexImportRequestFiltersType0 | Unset = UNSET
    limit: int | Unset = 100
    preview: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.open_alex_import_request_filters_type_0 import OpenAlexImportRequestFiltersType0

        domain = self.domain

        query = self.query

        filters: dict[str, Any] | None | Unset
        if isinstance(self.filters, Unset):
            filters = UNSET
        elif isinstance(self.filters, OpenAlexImportRequestFiltersType0):
            filters = self.filters.to_dict()
        else:
            filters = self.filters

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
        if filters is not UNSET:
            field_dict["filters"] = filters
        if limit is not UNSET:
            field_dict["limit"] = limit
        if preview is not UNSET:
            field_dict["preview"] = preview

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.open_alex_import_request_filters_type_0 import OpenAlexImportRequestFiltersType0

        d = dict(src_dict)
        domain = d.pop("domain")

        query = d.pop("query")

        def _parse_filters(data: object) -> None | OpenAlexImportRequestFiltersType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                filters_type_0 = OpenAlexImportRequestFiltersType0.from_dict(data)

                return filters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OpenAlexImportRequestFiltersType0 | Unset, data)

        filters = _parse_filters(d.pop("filters", UNSET))

        limit = d.pop("limit", UNSET)

        preview = d.pop("preview", UNSET)

        open_alex_import_request = cls(
            domain=domain,
            query=query,
            filters=filters,
            limit=limit,
            preview=preview,
        )

        open_alex_import_request.additional_properties = d
        return open_alex_import_request

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
