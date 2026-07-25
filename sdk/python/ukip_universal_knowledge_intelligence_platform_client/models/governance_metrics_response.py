from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ambiguous_source_metric import AmbiguousSourceMetric


T = TypeVar("T", bound="GovernanceMetricsResponse")


@_attrs_define
class GovernanceMetricsResponse:
    """
    Attributes:
        active_rules (int):
        inactive_rules (int):
        pending_suggestions (int):
        rejected_false_positives (int):
        ambiguous_sources (list[AmbiguousSourceMetric] | Unset):
        approved_rules (int | Unset):  Default: 0.
        needs_adjustment_rules (int | Unset):  Default: 0.
        pending_rules (int | Unset):  Default: 0.
        rejected_rules (int | Unset):  Default: 0.
    """

    active_rules: int
    inactive_rules: int
    pending_suggestions: int
    rejected_false_positives: int
    ambiguous_sources: list[AmbiguousSourceMetric] | Unset = UNSET
    approved_rules: int | Unset = 0
    needs_adjustment_rules: int | Unset = 0
    pending_rules: int | Unset = 0
    rejected_rules: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active_rules = self.active_rules

        inactive_rules = self.inactive_rules

        pending_suggestions = self.pending_suggestions

        rejected_false_positives = self.rejected_false_positives

        ambiguous_sources: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.ambiguous_sources, Unset):
            ambiguous_sources = []
            for ambiguous_sources_item_data in self.ambiguous_sources:
                ambiguous_sources_item = ambiguous_sources_item_data.to_dict()
                ambiguous_sources.append(ambiguous_sources_item)

        approved_rules = self.approved_rules

        needs_adjustment_rules = self.needs_adjustment_rules

        pending_rules = self.pending_rules

        rejected_rules = self.rejected_rules

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "active_rules": active_rules,
                "inactive_rules": inactive_rules,
                "pending_suggestions": pending_suggestions,
                "rejected_false_positives": rejected_false_positives,
            }
        )
        if ambiguous_sources is not UNSET:
            field_dict["ambiguous_sources"] = ambiguous_sources
        if approved_rules is not UNSET:
            field_dict["approved_rules"] = approved_rules
        if needs_adjustment_rules is not UNSET:
            field_dict["needs_adjustment_rules"] = needs_adjustment_rules
        if pending_rules is not UNSET:
            field_dict["pending_rules"] = pending_rules
        if rejected_rules is not UNSET:
            field_dict["rejected_rules"] = rejected_rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ambiguous_source_metric import AmbiguousSourceMetric

        d = dict(src_dict)
        active_rules = d.pop("active_rules")

        inactive_rules = d.pop("inactive_rules")

        pending_suggestions = d.pop("pending_suggestions")

        rejected_false_positives = d.pop("rejected_false_positives")

        _ambiguous_sources = d.pop("ambiguous_sources", UNSET)
        ambiguous_sources: list[AmbiguousSourceMetric] | Unset = UNSET
        if _ambiguous_sources is not UNSET:
            ambiguous_sources = []
            for ambiguous_sources_item_data in _ambiguous_sources:
                ambiguous_sources_item = AmbiguousSourceMetric.from_dict(ambiguous_sources_item_data)

                ambiguous_sources.append(ambiguous_sources_item)

        approved_rules = d.pop("approved_rules", UNSET)

        needs_adjustment_rules = d.pop("needs_adjustment_rules", UNSET)

        pending_rules = d.pop("pending_rules", UNSET)

        rejected_rules = d.pop("rejected_rules", UNSET)

        governance_metrics_response = cls(
            active_rules=active_rules,
            inactive_rules=inactive_rules,
            pending_suggestions=pending_suggestions,
            rejected_false_positives=rejected_false_positives,
            ambiguous_sources=ambiguous_sources,
            approved_rules=approved_rules,
            needs_adjustment_rules=needs_adjustment_rules,
            pending_rules=pending_rules,
            rejected_rules=rejected_rules,
        )

        governance_metrics_response.additional_properties = d
        return governance_metrics_response

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
