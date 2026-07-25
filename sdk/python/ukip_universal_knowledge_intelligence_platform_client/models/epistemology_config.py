from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evidence_level import EvidenceLevel
    from ..models.paradigm import Paradigm


T = TypeVar("T", bound="EpistemologyConfig")


@_attrs_define
class EpistemologyConfig:
    """
    Attributes:
        evidence_hierarchy (list[EvidenceLevel] | Unset):
        paradigms (list[Paradigm] | Unset):
    """

    evidence_hierarchy: list[EvidenceLevel] | Unset = UNSET
    paradigms: list[Paradigm] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        evidence_hierarchy: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.evidence_hierarchy, Unset):
            evidence_hierarchy = []
            for evidence_hierarchy_item_data in self.evidence_hierarchy:
                evidence_hierarchy_item = evidence_hierarchy_item_data.to_dict()
                evidence_hierarchy.append(evidence_hierarchy_item)

        paradigms: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.paradigms, Unset):
            paradigms = []
            for paradigms_item_data in self.paradigms:
                paradigms_item = paradigms_item_data.to_dict()
                paradigms.append(paradigms_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if evidence_hierarchy is not UNSET:
            field_dict["evidence_hierarchy"] = evidence_hierarchy
        if paradigms is not UNSET:
            field_dict["paradigms"] = paradigms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.evidence_level import EvidenceLevel
        from ..models.paradigm import Paradigm

        d = dict(src_dict)
        _evidence_hierarchy = d.pop("evidence_hierarchy", UNSET)
        evidence_hierarchy: list[EvidenceLevel] | Unset = UNSET
        if _evidence_hierarchy is not UNSET:
            evidence_hierarchy = []
            for evidence_hierarchy_item_data in _evidence_hierarchy:
                evidence_hierarchy_item = EvidenceLevel.from_dict(evidence_hierarchy_item_data)

                evidence_hierarchy.append(evidence_hierarchy_item)

        _paradigms = d.pop("paradigms", UNSET)
        paradigms: list[Paradigm] | Unset = UNSET
        if _paradigms is not UNSET:
            paradigms = []
            for paradigms_item_data in _paradigms:
                paradigms_item = Paradigm.from_dict(paradigms_item_data)

                paradigms.append(paradigms_item)

        epistemology_config = cls(
            evidence_hierarchy=evidence_hierarchy,
            paradigms=paradigms,
        )

        epistemology_config.additional_properties = d
        return epistemology_config

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
