from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_correspondence_rule_response import FieldCorrespondenceRuleResponse


T = TypeVar("T", bound="PreventiveRuleSeedResponse")


@_attrs_define
class PreventiveRuleSeedResponse:
    """
    Attributes:
        created (int):
        total_candidates (int):
        updated (int):
        rules (list[FieldCorrespondenceRuleResponse] | Unset):
    """

    created: int
    total_candidates: int
    updated: int
    rules: list[FieldCorrespondenceRuleResponse] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created = self.created

        total_candidates = self.total_candidates

        updated = self.updated

        rules: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.rules, Unset):
            rules = []
            for rules_item_data in self.rules:
                rules_item = rules_item_data.to_dict()
                rules.append(rules_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created": created,
                "total_candidates": total_candidates,
                "updated": updated,
            }
        )
        if rules is not UNSET:
            field_dict["rules"] = rules

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_correspondence_rule_response import FieldCorrespondenceRuleResponse

        d = dict(src_dict)
        created = d.pop("created")

        total_candidates = d.pop("total_candidates")

        updated = d.pop("updated")

        _rules = d.pop("rules", UNSET)
        rules: list[FieldCorrespondenceRuleResponse] | Unset = UNSET
        if _rules is not UNSET:
            rules = []
            for rules_item_data in _rules:
                rules_item = FieldCorrespondenceRuleResponse.from_dict(rules_item_data)

                rules.append(rules_item)

        preventive_rule_seed_response = cls(
            created=created,
            total_candidates=total_candidates,
            updated=updated,
            rules=rules,
        )

        preventive_rule_seed_response.additional_properties = d
        return preventive_rule_seed_response

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
