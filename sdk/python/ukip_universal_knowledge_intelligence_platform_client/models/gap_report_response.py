from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.gap_item_response import GapItemResponse
    from ..models.gap_report_response_summary import GapReportResponseSummary


T = TypeVar("T", bound="GapReportResponse")


@_attrs_define
class GapReportResponse:
    """
    Attributes:
        domain_id (str):
        gaps (list[GapItemResponse]):
        generated_at (datetime.datetime):
        summary (GapReportResponseSummary):
    """

    domain_id: str
    gaps: list[GapItemResponse]
    generated_at: datetime.datetime
    summary: GapReportResponseSummary
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        gaps = []
        for gaps_item_data in self.gaps:
            gaps_item = gaps_item_data.to_dict()
            gaps.append(gaps_item)

        generated_at = self.generated_at.isoformat()

        summary = self.summary.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "gaps": gaps,
                "generated_at": generated_at,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.gap_item_response import GapItemResponse
        from ..models.gap_report_response_summary import GapReportResponseSummary

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        gaps = []
        _gaps = d.pop("gaps")
        for gaps_item_data in _gaps:
            gaps_item = GapItemResponse.from_dict(gaps_item_data)

            gaps.append(gaps_item)

        generated_at = datetime.datetime.fromisoformat(d.pop("generated_at"))

        summary = GapReportResponseSummary.from_dict(d.pop("summary"))

        gap_report_response = cls(
            domain_id=domain_id,
            gaps=gaps,
            generated_at=generated_at,
            summary=summary,
        )

        gap_report_response.additional_properties = d
        return gap_report_response

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
