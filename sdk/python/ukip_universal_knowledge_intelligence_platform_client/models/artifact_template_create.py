from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ArtifactTemplateCreate")


@_attrs_define
class ArtifactTemplateCreate:
    """
    Attributes:
        name (str):
        sections (list[str]):
        default_title (str | Unset):  Default: ''.
        description (str | Unset):  Default: ''.
    """

    name: str
    sections: list[str]
    default_title: str | Unset = ""
    description: str | Unset = ""
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        sections = self.sections

        default_title = self.default_title

        description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "sections": sections,
            }
        )
        if default_title is not UNSET:
            field_dict["default_title"] = default_title
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        sections = cast(list[str], d.pop("sections"))

        default_title = d.pop("default_title", UNSET)

        description = d.pop("description", UNSET)

        artifact_template_create = cls(
            name=name,
            sections=sections,
            default_title=default_title,
            description=description,
        )

        artifact_template_create.additional_properties = d
        return artifact_template_create

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
