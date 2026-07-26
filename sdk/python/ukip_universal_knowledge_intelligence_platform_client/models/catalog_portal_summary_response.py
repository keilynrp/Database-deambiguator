from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog_portal_summary_response_source_context import CatalogPortalSummaryResponseSourceContext
    from ..models.catalog_portal_summary_response_summary import CatalogPortalSummaryResponseSummary


T = TypeVar("T", bound="CatalogPortalSummaryResponse")


@_attrs_define
class CatalogPortalSummaryResponse:
    """
    Attributes:
        default_order (str):
        default_sort (str):
        domain_id (str):
        featured_facets (list[str]):
        id (int):
        slug (str):
        summary (CatalogPortalSummaryResponseSummary):
        title (str):
        visibility (str):
        created_at (datetime.datetime | None | Unset):
        created_by (int | None | Unset):
        description (None | str | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_entity_type (None | str | Unset):
        ft_source (None | str | Unset):
        ft_validation_status (None | str | Unset):
        min_quality (float | None | Unset):
        org_id (int | None | Unset):
        search (None | str | Unset):
        source_batch_id (int | None | Unset):
        source_context (CatalogPortalSummaryResponseSourceContext | Unset):
        source_label (None | str | Unset):
        updated_at (datetime.datetime | None | Unset):
    """

    default_order: str
    default_sort: str
    domain_id: str
    featured_facets: list[str]
    id: int
    slug: str
    summary: CatalogPortalSummaryResponseSummary
    title: str
    visibility: str
    created_at: datetime.datetime | None | Unset = UNSET
    created_by: int | None | Unset = UNSET
    description: None | str | Unset = UNSET
    ft_enrichment_status: None | str | Unset = UNSET
    ft_entity_type: None | str | Unset = UNSET
    ft_source: None | str | Unset = UNSET
    ft_validation_status: None | str | Unset = UNSET
    min_quality: float | None | Unset = UNSET
    org_id: int | None | Unset = UNSET
    search: None | str | Unset = UNSET
    source_batch_id: int | None | Unset = UNSET
    source_context: CatalogPortalSummaryResponseSourceContext | Unset = UNSET
    source_label: None | str | Unset = UNSET
    updated_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        default_order = self.default_order

        default_sort = self.default_sort

        domain_id = self.domain_id

        featured_facets = self.featured_facets

        id = self.id

        slug = self.slug

        summary = self.summary.to_dict()

        title = self.title

        visibility = self.visibility

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        elif isinstance(self.created_at, datetime.datetime):
            created_at = self.created_at.isoformat()
        else:
            created_at = self.created_at

        created_by: int | None | Unset
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        ft_enrichment_status: None | str | Unset
        if isinstance(self.ft_enrichment_status, Unset):
            ft_enrichment_status = UNSET
        else:
            ft_enrichment_status = self.ft_enrichment_status

        ft_entity_type: None | str | Unset
        if isinstance(self.ft_entity_type, Unset):
            ft_entity_type = UNSET
        else:
            ft_entity_type = self.ft_entity_type

        ft_source: None | str | Unset
        if isinstance(self.ft_source, Unset):
            ft_source = UNSET
        else:
            ft_source = self.ft_source

        ft_validation_status: None | str | Unset
        if isinstance(self.ft_validation_status, Unset):
            ft_validation_status = UNSET
        else:
            ft_validation_status = self.ft_validation_status

        min_quality: float | None | Unset
        if isinstance(self.min_quality, Unset):
            min_quality = UNSET
        else:
            min_quality = self.min_quality

        org_id: int | None | Unset
        if isinstance(self.org_id, Unset):
            org_id = UNSET
        else:
            org_id = self.org_id

        search: None | str | Unset
        if isinstance(self.search, Unset):
            search = UNSET
        else:
            search = self.search

        source_batch_id: int | None | Unset
        if isinstance(self.source_batch_id, Unset):
            source_batch_id = UNSET
        else:
            source_batch_id = self.source_batch_id

        source_context: dict[str, Any] | Unset = UNSET
        if not isinstance(self.source_context, Unset):
            source_context = self.source_context.to_dict()

        source_label: None | str | Unset
        if isinstance(self.source_label, Unset):
            source_label = UNSET
        else:
            source_label = self.source_label

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        elif isinstance(self.updated_at, datetime.datetime):
            updated_at = self.updated_at.isoformat()
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "default_order": default_order,
                "default_sort": default_sort,
                "domain_id": domain_id,
                "featured_facets": featured_facets,
                "id": id,
                "slug": slug,
                "summary": summary,
                "title": title,
                "visibility": visibility,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if description is not UNSET:
            field_dict["description"] = description
        if ft_enrichment_status is not UNSET:
            field_dict["ft_enrichment_status"] = ft_enrichment_status
        if ft_entity_type is not UNSET:
            field_dict["ft_entity_type"] = ft_entity_type
        if ft_source is not UNSET:
            field_dict["ft_source"] = ft_source
        if ft_validation_status is not UNSET:
            field_dict["ft_validation_status"] = ft_validation_status
        if min_quality is not UNSET:
            field_dict["min_quality"] = min_quality
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if search is not UNSET:
            field_dict["search"] = search
        if source_batch_id is not UNSET:
            field_dict["source_batch_id"] = source_batch_id
        if source_context is not UNSET:
            field_dict["source_context"] = source_context
        if source_label is not UNSET:
            field_dict["source_label"] = source_label
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_portal_summary_response_source_context import CatalogPortalSummaryResponseSourceContext
        from ..models.catalog_portal_summary_response_summary import CatalogPortalSummaryResponseSummary

        d = dict(src_dict)
        default_order = d.pop("default_order")

        default_sort = d.pop("default_sort")

        domain_id = d.pop("domain_id")

        featured_facets = cast(list[str], d.pop("featured_facets"))

        id = d.pop("id")

        slug = d.pop("slug")

        summary = CatalogPortalSummaryResponseSummary.from_dict(d.pop("summary"))

        title = d.pop("title")

        visibility = d.pop("visibility")

        def _parse_created_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                created_at_type_0 = datetime.datetime.fromisoformat(data)

                return created_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_created_by(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        created_by = _parse_created_by(d.pop("created_by", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_ft_enrichment_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ft_enrichment_status = _parse_ft_enrichment_status(d.pop("ft_enrichment_status", UNSET))

        def _parse_ft_entity_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ft_entity_type = _parse_ft_entity_type(d.pop("ft_entity_type", UNSET))

        def _parse_ft_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ft_source = _parse_ft_source(d.pop("ft_source", UNSET))

        def _parse_ft_validation_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        ft_validation_status = _parse_ft_validation_status(d.pop("ft_validation_status", UNSET))

        def _parse_min_quality(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_quality = _parse_min_quality(d.pop("min_quality", UNSET))

        def _parse_org_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        org_id = _parse_org_id(d.pop("org_id", UNSET))

        def _parse_search(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        search = _parse_search(d.pop("search", UNSET))

        def _parse_source_batch_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        source_batch_id = _parse_source_batch_id(d.pop("source_batch_id", UNSET))

        _source_context = d.pop("source_context", UNSET)
        source_context: CatalogPortalSummaryResponseSourceContext | Unset
        if isinstance(_source_context, Unset):
            source_context = UNSET
        else:
            source_context = CatalogPortalSummaryResponseSourceContext.from_dict(_source_context)

        def _parse_source_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_label = _parse_source_label(d.pop("source_label", UNSET))

        def _parse_updated_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                updated_at_type_0 = datetime.datetime.fromisoformat(data)

                return updated_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        catalog_portal_summary_response = cls(
            default_order=default_order,
            default_sort=default_sort,
            domain_id=domain_id,
            featured_facets=featured_facets,
            id=id,
            slug=slug,
            summary=summary,
            title=title,
            visibility=visibility,
            created_at=created_at,
            created_by=created_by,
            description=description,
            ft_enrichment_status=ft_enrichment_status,
            ft_entity_type=ft_entity_type,
            ft_source=ft_source,
            ft_validation_status=ft_validation_status,
            min_quality=min_quality,
            org_id=org_id,
            search=search,
            source_batch_id=source_batch_id,
            source_context=source_context,
            source_label=source_label,
            updated_at=updated_at,
        )

        catalog_portal_summary_response.additional_properties = d
        return catalog_portal_summary_response

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
