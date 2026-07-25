from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.readiness_response_families import ReadinessResponseFamilies


T = TypeVar("T", bound="ReadinessResponse")


@_attrs_define
class ReadinessResponse:
    """
    Attributes:
        dataset_id (str):
        families (ReadinessResponseFamilies):
        state (str):
    """

    dataset_id: str
    families: ReadinessResponseFamilies
    state: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dataset_id = self.dataset_id

        families = self.families.to_dict()

        state = self.state

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dataset_id": dataset_id,
                "families": families,
                "state": state,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.readiness_response_families import ReadinessResponseFamilies

        d = dict(src_dict)
        dataset_id = d.pop("dataset_id")

        families = ReadinessResponseFamilies.from_dict(d.pop("families"))

        state = d.pop("state")

        readiness_response = cls(
            dataset_id=dataset_id,
            families=families,
            state=state,
        )

        readiness_response.additional_properties = d
        return readiness_response

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
