from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.manual_report_section import ManualReportSection


T = TypeVar("T", bound="ReportRequest")


@_attrs_define
class ReportRequest:
    """
    Attributes:
        benchmark_profile_id (None | str | Unset):
        domain_id (str | Unset):  Default: 'default'.
        manual_sections (list[ManualReportSection] | Unset):
        sections (list[str] | Unset):
        stakeholder_profile (None | str | Unset):  Default: 'leadership'.
        title (None | str | Unset):
    """

    benchmark_profile_id: None | str | Unset = UNSET
    domain_id: str | Unset = "default"
    manual_sections: list[ManualReportSection] | Unset = UNSET
    sections: list[str] | Unset = UNSET
    stakeholder_profile: None | str | Unset = "leadership"
    title: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        benchmark_profile_id: None | str | Unset
        if isinstance(self.benchmark_profile_id, Unset):
            benchmark_profile_id = UNSET
        else:
            benchmark_profile_id = self.benchmark_profile_id

        domain_id = self.domain_id

        manual_sections: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.manual_sections, Unset):
            manual_sections = []
            for manual_sections_item_data in self.manual_sections:
                manual_sections_item = manual_sections_item_data.to_dict()
                manual_sections.append(manual_sections_item)

        sections: list[str] | Unset = UNSET
        if not isinstance(self.sections, Unset):
            sections = self.sections

        stakeholder_profile: None | str | Unset
        if isinstance(self.stakeholder_profile, Unset):
            stakeholder_profile = UNSET
        else:
            stakeholder_profile = self.stakeholder_profile

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if benchmark_profile_id is not UNSET:
            field_dict["benchmark_profile_id"] = benchmark_profile_id
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if manual_sections is not UNSET:
            field_dict["manual_sections"] = manual_sections
        if sections is not UNSET:
            field_dict["sections"] = sections
        if stakeholder_profile is not UNSET:
            field_dict["stakeholder_profile"] = stakeholder_profile
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.manual_report_section import ManualReportSection

        d = dict(src_dict)

        def _parse_benchmark_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        benchmark_profile_id = _parse_benchmark_profile_id(d.pop("benchmark_profile_id", UNSET))

        domain_id = d.pop("domain_id", UNSET)

        _manual_sections = d.pop("manual_sections", UNSET)
        manual_sections: list[ManualReportSection] | Unset = UNSET
        if _manual_sections is not UNSET:
            manual_sections = []
            for manual_sections_item_data in _manual_sections:
                manual_sections_item = ManualReportSection.from_dict(manual_sections_item_data)

                manual_sections.append(manual_sections_item)

        sections = cast(list[str], d.pop("sections", UNSET))

        def _parse_stakeholder_profile(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        stakeholder_profile = _parse_stakeholder_profile(d.pop("stakeholder_profile", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        report_request = cls(
            benchmark_profile_id=benchmark_profile_id,
            domain_id=domain_id,
            manual_sections=manual_sections,
            sections=sections,
            stakeholder_profile=stakeholder_profile,
            title=title,
        )

        report_request.additional_properties = d
        return report_request

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
