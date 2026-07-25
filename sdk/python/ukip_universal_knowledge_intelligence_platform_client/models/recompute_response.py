from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.recompute_response_results_item import RecomputeResponseResultsItem


T = TypeVar("T", bound="RecomputeResponse")


@_attrs_define
class RecomputeResponse:
    """
    Attributes:
        domain_id (str):
        results (list[RecomputeResponseResultsItem]):
        scopes_recomputed (int): Number of (org, domain) scopes recomputed.
    """

    domain_id: str
    results: list[RecomputeResponseResultsItem]
    scopes_recomputed: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        scopes_recomputed = self.scopes_recomputed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "results": results,
                "scopes_recomputed": scopes_recomputed,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.recompute_response_results_item import RecomputeResponseResultsItem

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = RecomputeResponseResultsItem.from_dict(results_item_data)

            results.append(results_item)

        scopes_recomputed = d.pop("scopes_recomputed")

        recompute_response = cls(
            domain_id=domain_id,
            results=results,
            scopes_recomputed=scopes_recomputed,
        )

        recompute_response.additional_properties = d
        return recompute_response

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
