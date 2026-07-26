from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ArtifactTemplateResponse")


@_attrs_define
class ArtifactTemplateResponse:
    """
    Attributes:
        created_at (datetime.datetime):
        default_title (str):
        description (str):
        id (int):
        is_builtin (bool):
        name (str):
        sections (list[str]):
    """

    created_at: datetime.datetime
    default_title: str
    description: str
    id: int
    is_builtin: bool
    name: str
    sections: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        default_title = self.default_title

        description = self.description

        id = self.id

        is_builtin = self.is_builtin

        name = self.name

        sections = self.sections

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "default_title": default_title,
                "description": description,
                "id": id,
                "is_builtin": is_builtin,
                "name": name,
                "sections": sections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))

        default_title = d.pop("default_title")

        description = d.pop("description")

        id = d.pop("id")

        is_builtin = d.pop("is_builtin")

        name = d.pop("name")

        sections = cast(list[str], d.pop("sections"))

        artifact_template_response = cls(
            created_at=created_at,
            default_title=default_title,
            description=description,
            id=id,
            is_builtin=is_builtin,
            name=name,
            sections=sections,
        )

        artifact_template_response.additional_properties = d
        return artifact_template_response

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
