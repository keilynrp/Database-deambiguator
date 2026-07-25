from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduledReportCreate")


@_attrs_define
class ScheduledReportCreate:
    """
    Attributes:
        name (str):
        domain_id (str | Unset):  Default: 'default'.
        format_ (str | Unset):  Default: 'pdf'.
        interval_minutes (int | Unset):  Default: 1440.
        recipient_emails (list[str] | Unset):
        report_title (None | str | Unset):
        sections (list[str] | Unset):
    """

    name: str
    domain_id: str | Unset = "default"
    format_: str | Unset = "pdf"
    interval_minutes: int | Unset = 1440
    recipient_emails: list[str] | Unset = UNSET
    report_title: None | str | Unset = UNSET
    sections: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        domain_id = self.domain_id

        format_ = self.format_

        interval_minutes = self.interval_minutes

        recipient_emails: list[str] | Unset = UNSET
        if not isinstance(self.recipient_emails, Unset):
            recipient_emails = self.recipient_emails

        report_title: None | str | Unset
        if isinstance(self.report_title, Unset):
            report_title = UNSET
        else:
            report_title = self.report_title

        sections: list[str] | Unset = UNSET
        if not isinstance(self.sections, Unset):
            sections = self.sections

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if format_ is not UNSET:
            field_dict["format"] = format_
        if interval_minutes is not UNSET:
            field_dict["interval_minutes"] = interval_minutes
        if recipient_emails is not UNSET:
            field_dict["recipient_emails"] = recipient_emails
        if report_title is not UNSET:
            field_dict["report_title"] = report_title
        if sections is not UNSET:
            field_dict["sections"] = sections

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        domain_id = d.pop("domain_id", UNSET)

        format_ = d.pop("format", UNSET)

        interval_minutes = d.pop("interval_minutes", UNSET)

        recipient_emails = cast(list[str], d.pop("recipient_emails", UNSET))

        def _parse_report_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        report_title = _parse_report_title(d.pop("report_title", UNSET))

        sections = cast(list[str], d.pop("sections", UNSET))

        scheduled_report_create = cls(
            name=name,
            domain_id=domain_id,
            format_=format_,
            interval_minutes=interval_minutes,
            recipient_emails=recipient_emails,
            report_title=report_title,
            sections=sections,
        )

        scheduled_report_create.additional_properties = d
        return scheduled_report_create

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
