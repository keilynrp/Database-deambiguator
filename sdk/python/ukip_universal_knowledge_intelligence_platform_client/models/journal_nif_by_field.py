from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JournalNifByField")


@_attrs_define
class JournalNifByField:
    """
    Attributes:
        journal_count (int):
        mean_nif (float):
        nif_field (None | str | Unset):
    """

    journal_count: int
    mean_nif: float
    nif_field: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        journal_count = self.journal_count

        mean_nif = self.mean_nif

        nif_field: None | str | Unset
        if isinstance(self.nif_field, Unset):
            nif_field = UNSET
        else:
            nif_field = self.nif_field

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "journal_count": journal_count,
                "mean_nif": mean_nif,
            }
        )
        if nif_field is not UNSET:
            field_dict["nif_field"] = nif_field

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        journal_count = d.pop("journal_count")

        mean_nif = d.pop("mean_nif")

        def _parse_nif_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        nif_field = _parse_nif_field(d.pop("nif_field", UNSET))

        journal_nif_by_field = cls(
            journal_count=journal_count,
            mean_nif=mean_nif,
            nif_field=nif_field,
        )

        journal_nif_by_field.additional_properties = d
        return journal_nif_by_field

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
