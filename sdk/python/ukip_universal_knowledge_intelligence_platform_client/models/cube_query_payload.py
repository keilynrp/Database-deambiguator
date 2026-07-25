from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cube_query_payload_filters import CubeQueryPayloadFilters


T = TypeVar("T", bound="CubeQueryPayload")


@_attrs_define
class CubeQueryPayload:
    """
    Attributes:
        domain_id (str):
        group_by (list[str]):
        filters (CubeQueryPayloadFilters | Unset):
    """

    domain_id: str
    group_by: list[str]
    filters: CubeQueryPayloadFilters | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        group_by = self.group_by

        filters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.filters, Unset):
            filters = self.filters.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "group_by": group_by,
            }
        )
        if filters is not UNSET:
            field_dict["filters"] = filters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.cube_query_payload_filters import CubeQueryPayloadFilters

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        group_by = cast(list[str], d.pop("group_by"))

        _filters = d.pop("filters", UNSET)
        filters: CubeQueryPayloadFilters | Unset
        if isinstance(_filters, Unset):
            filters = UNSET
        else:
            filters = CubeQueryPayloadFilters.from_dict(_filters)

        cube_query_payload = cls(
            domain_id=domain_id,
            group_by=group_by,
            filters=filters,
        )

        cube_query_payload.additional_properties = d
        return cube_query_payload

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
