from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.profile_request_sample_values import ProfileRequestSampleValues


T = TypeVar("T", bound="ProfileRequest")


@_attrs_define
class ProfileRequest:
    """
    Attributes:
        source_id (str):
        field_names (list[str] | Unset):
        payload_type (str | Unset):  Default: 'csv'.
        sample_values (ProfileRequestSampleValues | Unset):
    """

    source_id: str
    field_names: list[str] | Unset = UNSET
    payload_type: str | Unset = "csv"
    sample_values: ProfileRequestSampleValues | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_id = self.source_id

        field_names: list[str] | Unset = UNSET
        if not isinstance(self.field_names, Unset):
            field_names = self.field_names

        payload_type = self.payload_type

        sample_values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.sample_values, Unset):
            sample_values = self.sample_values.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_id": source_id,
            }
        )
        if field_names is not UNSET:
            field_dict["field_names"] = field_names
        if payload_type is not UNSET:
            field_dict["payload_type"] = payload_type
        if sample_values is not UNSET:
            field_dict["sample_values"] = sample_values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_request_sample_values import ProfileRequestSampleValues

        d = dict(src_dict)
        source_id = d.pop("source_id")

        field_names = cast(list[str], d.pop("field_names", UNSET))

        payload_type = d.pop("payload_type", UNSET)

        _sample_values = d.pop("sample_values", UNSET)
        sample_values: ProfileRequestSampleValues | Unset
        if isinstance(_sample_values, Unset):
            sample_values = UNSET
        else:
            sample_values = ProfileRequestSampleValues.from_dict(_sample_values)

        profile_request = cls(
            source_id=source_id,
            field_names=field_names,
            payload_type=payload_type,
            sample_values=sample_values,
        )

        profile_request.additional_properties = d
        return profile_request

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
