from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ResolutionThresholdCreate")


@_attrs_define
class ResolutionThresholdCreate:
    """Create/update an adaptive resolution-threshold override (Task 11).

    Attributes:
        ambiguous (float):
        exact (float):
        field_name (str):
        probable (float):
        domain_id (None | str | Unset):
    """

    ambiguous: float
    exact: float
    field_name: str
    probable: float
    domain_id: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        ambiguous = self.ambiguous

        exact = self.exact

        field_name = self.field_name

        probable = self.probable

        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        else:
            domain_id = self.domain_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ambiguous": ambiguous,
                "exact": exact,
                "field_name": field_name,
                "probable": probable,
            }
        )
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        ambiguous = d.pop("ambiguous")

        exact = d.pop("exact")

        field_name = d.pop("field_name")

        probable = d.pop("probable")

        def _parse_domain_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        resolution_threshold_create = cls(
            ambiguous=ambiguous,
            exact=exact,
            field_name=field_name,
            probable=probable,
            domain_id=domain_id,
        )

        resolution_threshold_create.additional_properties = d
        return resolution_threshold_create

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
