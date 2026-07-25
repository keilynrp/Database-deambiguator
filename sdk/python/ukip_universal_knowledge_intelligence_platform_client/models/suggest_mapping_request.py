from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.suggest_mapping_request_sample_rows_item import SuggestMappingRequestSampleRowsItem


T = TypeVar("T", bound="SuggestMappingRequest")


@_attrs_define
class SuggestMappingRequest:
    """
    Attributes:
        columns (list[str]):
        sample_rows (list[SuggestMappingRequestSampleRowsItem] | Unset):
    """

    columns: list[str]
    sample_rows: list[SuggestMappingRequestSampleRowsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        columns = self.columns

        sample_rows: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sample_rows, Unset):
            sample_rows = []
            for sample_rows_item_data in self.sample_rows:
                sample_rows_item = sample_rows_item_data.to_dict()
                sample_rows.append(sample_rows_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "columns": columns,
            }
        )
        if sample_rows is not UNSET:
            field_dict["sample_rows"] = sample_rows

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.suggest_mapping_request_sample_rows_item import SuggestMappingRequestSampleRowsItem

        d = dict(src_dict)
        columns = cast(list[str], d.pop("columns"))

        _sample_rows = d.pop("sample_rows", UNSET)
        sample_rows: list[SuggestMappingRequestSampleRowsItem] | Unset = UNSET
        if _sample_rows is not UNSET:
            sample_rows = []
            for sample_rows_item_data in _sample_rows:
                sample_rows_item = SuggestMappingRequestSampleRowsItem.from_dict(sample_rows_item_data)

                sample_rows.append(sample_rows_item)

        suggest_mapping_request = cls(
            columns=columns,
            sample_rows=sample_rows,
        )

        suggest_mapping_request.additional_properties = d
        return suggest_mapping_request

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
