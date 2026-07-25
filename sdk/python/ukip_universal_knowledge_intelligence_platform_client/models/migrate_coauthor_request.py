from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MigrateCoauthorRequest")


@_attrs_define
class MigrateCoauthorRequest:
    """
    Attributes:
        domain (None | str | Unset): Restrict to one domain_id. None = all domains.
        dry_run (bool | Unset): Scan + report counts without writing. Defaults true for safety. Default: True.
    """

    domain: None | str | Unset = UNSET
    dry_run: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain: None | str | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        dry_run = self.dry_run

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain is not UNSET:
            field_dict["domain"] = domain
        if dry_run is not UNSET:
            field_dict["dry_run"] = dry_run

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_domain(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        dry_run = d.pop("dry_run", UNSET)

        migrate_coauthor_request = cls(
            domain=domain,
            dry_run=dry_run,
        )

        migrate_coauthor_request.additional_properties = d
        return migrate_coauthor_request

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
