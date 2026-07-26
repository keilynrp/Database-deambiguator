from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attribute_schema import AttributeSchema
    from ..models.discourse_config import DiscourseConfig
    from ..models.epistemology_config import EpistemologyConfig


T = TypeVar("T", bound="DomainSchema")


@_attrs_define
class DomainSchema:
    """
    Attributes:
        attributes (list[AttributeSchema]):
        description (str):
        id (str):
        name (str):
        primary_entity (str):
        discourse_community (DiscourseConfig | None | Unset):
        entity_count (int | None | Unset):
        epistemology (EpistemologyConfig | None | Unset):
        first_entity_id (int | None | Unset):
        icon (None | str | Unset):  Default: 'Database'.
    """

    attributes: list[AttributeSchema]
    description: str
    id: str
    name: str
    primary_entity: str
    discourse_community: DiscourseConfig | None | Unset = UNSET
    entity_count: int | None | Unset = UNSET
    epistemology: EpistemologyConfig | None | Unset = UNSET
    first_entity_id: int | None | Unset = UNSET
    icon: None | str | Unset = "Database"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.discourse_config import DiscourseConfig
        from ..models.epistemology_config import EpistemologyConfig

        attributes = []
        for attributes_item_data in self.attributes:
            attributes_item = attributes_item_data.to_dict()
            attributes.append(attributes_item)

        description = self.description

        id = self.id

        name = self.name

        primary_entity = self.primary_entity

        discourse_community: dict[str, Any] | None | Unset
        if isinstance(self.discourse_community, Unset):
            discourse_community = UNSET
        elif isinstance(self.discourse_community, DiscourseConfig):
            discourse_community = self.discourse_community.to_dict()
        else:
            discourse_community = self.discourse_community

        entity_count: int | None | Unset
        if isinstance(self.entity_count, Unset):
            entity_count = UNSET
        else:
            entity_count = self.entity_count

        epistemology: dict[str, Any] | None | Unset
        if isinstance(self.epistemology, Unset):
            epistemology = UNSET
        elif isinstance(self.epistemology, EpistemologyConfig):
            epistemology = self.epistemology.to_dict()
        else:
            epistemology = self.epistemology

        first_entity_id: int | None | Unset
        if isinstance(self.first_entity_id, Unset):
            first_entity_id = UNSET
        else:
            first_entity_id = self.first_entity_id

        icon: None | str | Unset
        if isinstance(self.icon, Unset):
            icon = UNSET
        else:
            icon = self.icon

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributes": attributes,
                "description": description,
                "id": id,
                "name": name,
                "primary_entity": primary_entity,
            }
        )
        if discourse_community is not UNSET:
            field_dict["discourse_community"] = discourse_community
        if entity_count is not UNSET:
            field_dict["entity_count"] = entity_count
        if epistemology is not UNSET:
            field_dict["epistemology"] = epistemology
        if first_entity_id is not UNSET:
            field_dict["first_entity_id"] = first_entity_id
        if icon is not UNSET:
            field_dict["icon"] = icon

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attribute_schema import AttributeSchema
        from ..models.discourse_config import DiscourseConfig
        from ..models.epistemology_config import EpistemologyConfig

        d = dict(src_dict)
        attributes = []
        _attributes = d.pop("attributes")
        for attributes_item_data in _attributes:
            attributes_item = AttributeSchema.from_dict(attributes_item_data)

            attributes.append(attributes_item)

        description = d.pop("description")

        id = d.pop("id")

        name = d.pop("name")

        primary_entity = d.pop("primary_entity")

        def _parse_discourse_community(data: object) -> DiscourseConfig | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                discourse_community_type_0 = DiscourseConfig.from_dict(data)

                return discourse_community_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DiscourseConfig | None | Unset, data)

        discourse_community = _parse_discourse_community(d.pop("discourse_community", UNSET))

        def _parse_entity_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        entity_count = _parse_entity_count(d.pop("entity_count", UNSET))

        def _parse_epistemology(data: object) -> EpistemologyConfig | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                epistemology_type_0 = EpistemologyConfig.from_dict(data)

                return epistemology_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EpistemologyConfig | None | Unset, data)

        epistemology = _parse_epistemology(d.pop("epistemology", UNSET))

        def _parse_first_entity_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        first_entity_id = _parse_first_entity_id(d.pop("first_entity_id", UNSET))

        def _parse_icon(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        icon = _parse_icon(d.pop("icon", UNSET))

        domain_schema = cls(
            attributes=attributes,
            description=description,
            id=id,
            name=name,
            primary_entity=primary_entity,
            discourse_community=discourse_community,
            entity_count=entity_count,
            epistemology=epistemology,
            first_entity_id=first_entity_id,
            icon=icon,
        )

        domain_schema.additional_properties = d
        return domain_schema

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
