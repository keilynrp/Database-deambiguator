from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.catalog_portal_create_default_order import CatalogPortalCreateDefaultOrder
from ..models.catalog_portal_create_default_sort import CatalogPortalCreateDefaultSort
from ..models.catalog_portal_create_visibility import CatalogPortalCreateVisibility
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog_portal_create_source_context import CatalogPortalCreateSourceContext


T = TypeVar("T", bound="CatalogPortalCreate")


@_attrs_define
class CatalogPortalCreate:
    """
    Attributes:
        domain_id (str):
        slug (str):
        title (str):
        default_order (CatalogPortalCreateDefaultOrder | Unset):  Default: CatalogPortalCreateDefaultOrder.ASC.
        default_sort (CatalogPortalCreateDefaultSort | Unset):  Default: CatalogPortalCreateDefaultSort.PRIMARY_LABEL.
        description (None | str | Unset):
        featured_facets (list[str] | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_entity_type (None | str | Unset):
        ft_source (None | str | Unset):
        ft_validation_status (None | str | Unset):
        min_quality (float | None | Unset):
        search (None | str | Unset):
        source_batch_id (int | None | Unset):
        source_context (CatalogPortalCreateSourceContext | Unset):
        source_label (None | str | Unset):
        visibility (CatalogPortalCreateVisibility | Unset):  Default: CatalogPortalCreateVisibility.PRIVATE.
    """

    domain_id: str
    slug: str
    title: str
    default_order: CatalogPortalCreateDefaultOrder | Unset = CatalogPortalCreateDefaultOrder.ASC
    default_sort: CatalogPortalCreateDefaultSort | Unset = CatalogPortalCreateDefaultSort.PRIMARY_LABEL
    description: None | str | Unset = UNSET
    featured_facets: list[str] | Unset = UNSET
    ft_enrichment_status: None | str | Unset = UNSET
    ft_entity_type: None | str | Unset = UNSET
    ft_source: None | str | Unset = UNSET
    ft_validation_status: None | str | Unset = UNSET
    min_quality: float | None | Unset = UNSET
    search: None | str | Unset = UNSET
    source_batch_id: int | None | Unset = UNSET
    source_context: CatalogPortalCreateSourceContext | Unset = UNSET
    source_label: None | str | Unset = UNSET
    visibility: CatalogPortalCreateVisibility | Unset = CatalogPortalCreateVisibility.PRIVATE
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        slug = self.slug

        title = self.title

        default_order: str | Unset = UNSET
        if not isinstance(self.default_order, Unset):
            default_order = self.default_order.value

        default_sort: str | Unset = UNSET
        if not isinstance(self.default_sort, Unset):
            default_sort = self.default_sort.value

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        featured_facets: list[str] | Unset = UNSET
        if not isinstance(self.featured_facets, Unset):
            featured_facets = self.featured_facets

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

        visibility: str | Unset = UNSET
        if not isinstance(self.visibility, Unset):
            visibility = self.visibility.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "slug": slug,
                "title": title,
            }
        )
        if default_order is not UNSET:
            field_dict["default_order"] = default_order
        if default_sort is not UNSET:
            field_dict["default_sort"] = default_sort
        if description is not UNSET:
            field_dict["description"] = description
        if featured_facets is not UNSET:
            field_dict["featured_facets"] = featured_facets
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
        if search is not UNSET:
            field_dict["search"] = search
        if source_batch_id is not UNSET:
            field_dict["source_batch_id"] = source_batch_id
        if source_context is not UNSET:
            field_dict["source_context"] = source_context
        if source_label is not UNSET:
            field_dict["source_label"] = source_label
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_portal_create_source_context import CatalogPortalCreateSourceContext

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        slug = d.pop("slug")

        title = d.pop("title")

        _default_order = d.pop("default_order", UNSET)
        default_order: CatalogPortalCreateDefaultOrder | Unset
        if isinstance(_default_order, Unset):
            default_order = UNSET
        else:
            default_order = CatalogPortalCreateDefaultOrder(_default_order)

        _default_sort = d.pop("default_sort", UNSET)
        default_sort: CatalogPortalCreateDefaultSort | Unset
        if isinstance(_default_sort, Unset):
            default_sort = UNSET
        else:
            default_sort = CatalogPortalCreateDefaultSort(_default_sort)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        featured_facets = cast(list[str], d.pop("featured_facets", UNSET))

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
        source_context: CatalogPortalCreateSourceContext | Unset
        if isinstance(_source_context, Unset):
            source_context = UNSET
        else:
            source_context = CatalogPortalCreateSourceContext.from_dict(_source_context)

        def _parse_source_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_label = _parse_source_label(d.pop("source_label", UNSET))

        _visibility = d.pop("visibility", UNSET)
        visibility: CatalogPortalCreateVisibility | Unset
        if isinstance(_visibility, Unset):
            visibility = UNSET
        else:
            visibility = CatalogPortalCreateVisibility(_visibility)

        catalog_portal_create = cls(
            domain_id=domain_id,
            slug=slug,
            title=title,
            default_order=default_order,
            default_sort=default_sort,
            description=description,
            featured_facets=featured_facets,
            ft_enrichment_status=ft_enrichment_status,
            ft_entity_type=ft_entity_type,
            ft_source=ft_source,
            ft_validation_status=ft_validation_status,
            min_quality=min_quality,
            search=search,
            source_batch_id=source_batch_id,
            source_context=source_context,
            source_label=source_label,
            visibility=visibility,
        )

        catalog_portal_create.additional_properties = d
        return catalog_portal_create

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
