from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.source_stats_entry import SourceStatsEntry


T = TypeVar("T", bound="SourceStatsResponse")


@_attrs_define
class SourceStatsResponse:
    """Response for GET /enrichment/sources/stats.

    Attributes:
        domain_id (None | str):
        entries (list[SourceStatsEntry]):
    """

    domain_id: None | str
    entries: list[SourceStatsEntry]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id: None | str
        domain_id = self.domain_id

        entries = []
        for entries_item_data in self.entries:
            entries_item = entries_item_data.to_dict()
            entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "entries": entries,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_stats_entry import SourceStatsEntry

        d = dict(src_dict)

        def _parse_domain_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        domain_id = _parse_domain_id(d.pop("domain_id"))

        entries = []
        _entries = d.pop("entries")
        for entries_item_data in _entries:
            entries_item = SourceStatsEntry.from_dict(entries_item_data)

            entries.append(entries_item)

        source_stats_response = cls(
            domain_id=domain_id,
            entries=entries,
        )

        source_stats_response.additional_properties = d
        return source_stats_response

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
