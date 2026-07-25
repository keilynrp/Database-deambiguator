from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.epistemology_patch_evidence_hierarchy_item import EpistemologyPatchEvidenceHierarchyItem
    from ..models.paradigm_payload import ParadigmPayload


T = TypeVar("T", bound="EpistemologyPatch")


@_attrs_define
class EpistemologyPatch:
    """
    Attributes:
        evidence_hierarchy (list[EpistemologyPatchEvidenceHierarchyItem] | Unset):
        paradigms (list[ParadigmPayload] | Unset):
    """

    evidence_hierarchy: list[EpistemologyPatchEvidenceHierarchyItem] | Unset = UNSET
    paradigms: list[ParadigmPayload] | Unset = UNSET
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
        from ..models.epistemology_patch_evidence_hierarchy_item import EpistemologyPatchEvidenceHierarchyItem
        from ..models.paradigm_payload import ParadigmPayload

        d = dict(src_dict)
        _evidence_hierarchy = d.pop("evidence_hierarchy", UNSET)
        evidence_hierarchy: list[EpistemologyPatchEvidenceHierarchyItem] | Unset = UNSET
        if _evidence_hierarchy is not UNSET:
            evidence_hierarchy = []
            for evidence_hierarchy_item_data in _evidence_hierarchy:
                evidence_hierarchy_item = EpistemologyPatchEvidenceHierarchyItem.from_dict(evidence_hierarchy_item_data)

                evidence_hierarchy.append(evidence_hierarchy_item)

        _paradigms = d.pop("paradigms", UNSET)
        paradigms: list[ParadigmPayload] | Unset = UNSET
        if _paradigms is not UNSET:
            paradigms = []
            for paradigms_item_data in _paradigms:
                paradigms_item = ParadigmPayload.from_dict(paradigms_item_data)

                paradigms.append(paradigms_item)

        epistemology_patch = cls(
            evidence_hierarchy=evidence_hierarchy,
            paradigms=paradigms,
        )

        epistemology_patch.additional_properties = d
        return epistemology_patch

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
