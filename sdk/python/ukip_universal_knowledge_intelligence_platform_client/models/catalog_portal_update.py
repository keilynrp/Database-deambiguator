from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.catalog_portal_update_default_order_type_0 import CatalogPortalUpdateDefaultOrderType0
from ..models.catalog_portal_update_default_sort_type_0 import CatalogPortalUpdateDefaultSortType0
from ..models.catalog_portal_update_visibility_type_0 import CatalogPortalUpdateVisibilityType0
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog_portal_update_source_context_type_0 import CatalogPortalUpdateSourceContextType0


T = TypeVar("T", bound="CatalogPortalUpdate")


@_attrs_define
class CatalogPortalUpdate:
    """
    Attributes:
        default_order (CatalogPortalUpdateDefaultOrderType0 | None | Unset):
        default_sort (CatalogPortalUpdateDefaultSortType0 | None | Unset):
        description (None | str | Unset):
        featured_facets (list[str] | None | Unset):
        ft_enrichment_status (None | str | Unset):
        ft_entity_type (None | str | Unset):
        ft_source (None | str | Unset):
        ft_validation_status (None | str | Unset):
        min_quality (float | None | Unset):
        search (None | str | Unset):
        source_batch_id (int | None | Unset):
        source_context (CatalogPortalUpdateSourceContextType0 | None | Unset):
        source_label (None | str | Unset):
        title (None | str | Unset):
        visibility (CatalogPortalUpdateVisibilityType0 | None | Unset):
    """

    default_order: CatalogPortalUpdateDefaultOrderType0 | None | Unset = UNSET
    default_sort: CatalogPortalUpdateDefaultSortType0 | None | Unset = UNSET
    description: None | str | Unset = UNSET
    featured_facets: list[str] | None | Unset = UNSET
    ft_enrichment_status: None | str | Unset = UNSET
    ft_entity_type: None | str | Unset = UNSET
    ft_source: None | str | Unset = UNSET
    ft_validation_status: None | str | Unset = UNSET
    min_quality: float | None | Unset = UNSET
    search: None | str | Unset = UNSET
    source_batch_id: int | None | Unset = UNSET
    source_context: CatalogPortalUpdateSourceContextType0 | None | Unset = UNSET
    source_label: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    visibility: CatalogPortalUpdateVisibilityType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.catalog_portal_update_source_context_type_0 import CatalogPortalUpdateSourceContextType0

        default_order: None | str | Unset
        if isinstance(self.default_order, Unset):
            default_order = UNSET
        elif isinstance(self.default_order, CatalogPortalUpdateDefaultOrderType0):
            default_order = self.default_order.value
        else:
            default_order = self.default_order

        default_sort: None | str | Unset
        if isinstance(self.default_sort, Unset):
            default_sort = UNSET
        elif isinstance(self.default_sort, CatalogPortalUpdateDefaultSortType0):
            default_sort = self.default_sort.value
        else:
            default_sort = self.default_sort

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        featured_facets: list[str] | None | Unset
        if isinstance(self.featured_facets, Unset):
            featured_facets = UNSET
        elif isinstance(self.featured_facets, list):
            featured_facets = self.featured_facets

        else:
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

        source_context: dict[str, Any] | None | Unset
        if isinstance(self.source_context, Unset):
            source_context = UNSET
        elif isinstance(self.source_context, CatalogPortalUpdateSourceContextType0):
            source_context = self.source_context.to_dict()
        else:
            source_context = self.source_context

        source_label: None | str | Unset
        if isinstance(self.source_label, Unset):
            source_label = UNSET
        else:
            source_label = self.source_label

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        elif isinstance(self.visibility, CatalogPortalUpdateVisibilityType0):
            visibility = self.visibility.value
        else:
            visibility = self.visibility

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
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
        if title is not UNSET:
            field_dict["title"] = title
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_portal_update_source_context_type_0 import CatalogPortalUpdateSourceContextType0

        d = dict(src_dict)

        def _parse_default_order(data: object) -> CatalogPortalUpdateDefaultOrderType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                default_order_type_0 = CatalogPortalUpdateDefaultOrderType0(data)

                return default_order_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CatalogPortalUpdateDefaultOrderType0 | None | Unset, data)

        default_order = _parse_default_order(d.pop("default_order", UNSET))

        def _parse_default_sort(data: object) -> CatalogPortalUpdateDefaultSortType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                default_sort_type_0 = CatalogPortalUpdateDefaultSortType0(data)

                return default_sort_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CatalogPortalUpdateDefaultSortType0 | None | Unset, data)

        default_sort = _parse_default_sort(d.pop("default_sort", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_featured_facets(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                featured_facets_type_0 = cast(list[str], data)

                return featured_facets_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        featured_facets = _parse_featured_facets(d.pop("featured_facets", UNSET))

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

        def _parse_source_context(data: object) -> CatalogPortalUpdateSourceContextType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                source_context_type_0 = CatalogPortalUpdateSourceContextType0.from_dict(data)

                return source_context_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CatalogPortalUpdateSourceContextType0 | None | Unset, data)

        source_context = _parse_source_context(d.pop("source_context", UNSET))

        def _parse_source_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_label = _parse_source_label(d.pop("source_label", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_visibility(data: object) -> CatalogPortalUpdateVisibilityType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                visibility_type_0 = CatalogPortalUpdateVisibilityType0(data)

                return visibility_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CatalogPortalUpdateVisibilityType0 | None | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))

        catalog_portal_update = cls(
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
            title=title,
            visibility=visibility,
        )

        catalog_portal_update.additional_properties = d
        return catalog_portal_update

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
