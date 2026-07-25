from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, Unset

T = TypeVar("T", bound="BodyPostUpload")


@_attrs_define
class BodyPostUpload:
    """
    Attributes:
        file (str):
        domain (str | Unset):  Default: 'default'.
        field_mapping (str | Unset):  Default: '{}'.
    """

    file: str
    domain: str | Unset = "default"
    field_mapping: str | Unset = "{}"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        file = self.file

        domain = self.domain

        field_mapping = self.field_mapping

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "file": file,
            }
        )
        if domain is not UNSET:
            field_dict["domain"] = domain
        if field_mapping is not UNSET:
            field_dict["field_mapping"] = field_mapping

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        files.append(("file", (None, str(self.file).encode(), "text/plain")))

        if not isinstance(self.domain, Unset):
            files.append(("domain", (None, str(self.domain).encode(), "text/plain")))

        if not isinstance(self.field_mapping, Unset):
            files.append(("field_mapping", (None, str(self.field_mapping).encode(), "text/plain")))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        file = d.pop("file")

        domain = d.pop("domain", UNSET)

        field_mapping = d.pop("field_mapping", UNSET)

        body_post_upload = cls(
            file=file,
            domain=domain,
            field_mapping=field_mapping,
        )

        body_post_upload.additional_properties = d
        return body_post_upload

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
