from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.journal_apc_bucket import JournalApcBucket
    from ..models.journal_nif_by_field import JournalNifByField
    from ..models.journal_oa_share import JournalOAShare


T = TypeVar("T", bound="JournalStatsResponse")


@_attrs_define
class JournalStatsResponse:
    """
    Attributes:
        apc_distribution (list[JournalApcBucket]):
        nif_by_field (list[JournalNifByField]):
        open_access_share (JournalOAShare):
    """

    apc_distribution: list[JournalApcBucket]
    nif_by_field: list[JournalNifByField]
    open_access_share: JournalOAShare
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        apc_distribution = []
        for apc_distribution_item_data in self.apc_distribution:
            apc_distribution_item = apc_distribution_item_data.to_dict()
            apc_distribution.append(apc_distribution_item)

        nif_by_field = []
        for nif_by_field_item_data in self.nif_by_field:
            nif_by_field_item = nif_by_field_item_data.to_dict()
            nif_by_field.append(nif_by_field_item)

        open_access_share = self.open_access_share.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "apc_distribution": apc_distribution,
                "nif_by_field": nif_by_field,
                "open_access_share": open_access_share,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.journal_apc_bucket import JournalApcBucket
        from ..models.journal_nif_by_field import JournalNifByField
        from ..models.journal_oa_share import JournalOAShare

        d = dict(src_dict)
        apc_distribution = []
        _apc_distribution = d.pop("apc_distribution")
        for apc_distribution_item_data in _apc_distribution:
            apc_distribution_item = JournalApcBucket.from_dict(apc_distribution_item_data)

            apc_distribution.append(apc_distribution_item)

        nif_by_field = []
        _nif_by_field = d.pop("nif_by_field")
        for nif_by_field_item_data in _nif_by_field:
            nif_by_field_item = JournalNifByField.from_dict(nif_by_field_item_data)

            nif_by_field.append(nif_by_field_item)

        open_access_share = JournalOAShare.from_dict(d.pop("open_access_share"))

        journal_stats_response = cls(
            apc_distribution=apc_distribution,
            nif_by_field=nif_by_field,
            open_access_share=open_access_share,
        )

        journal_stats_response.additional_properties = d
        return journal_stats_response

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
