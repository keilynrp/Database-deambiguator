from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ScheduledReportUpdate")


@_attrs_define
class ScheduledReportUpdate:
    """
    Attributes:
        domain_id (None | str | Unset):
        format_ (None | str | Unset):
        interval_minutes (int | None | Unset):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        recipient_emails (list[str] | None | Unset):
        report_title (None | str | Unset):
        sections (list[str] | None | Unset):
    """

    domain_id: None | str | Unset = UNSET
    format_: None | str | Unset = UNSET
    interval_minutes: int | None | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    recipient_emails: list[str] | None | Unset = UNSET
    report_title: None | str | Unset = UNSET
    sections: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        else:
            domain_id = self.domain_id

        format_: None | str | Unset
        if isinstance(self.format_, Unset):
            format_ = UNSET
        else:
            format_ = self.format_

        interval_minutes: int | None | Unset
        if isinstance(self.interval_minutes, Unset):
            interval_minutes = UNSET
        else:
            interval_minutes = self.interval_minutes

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        recipient_emails: list[str] | None | Unset
        if isinstance(self.recipient_emails, Unset):
            recipient_emails = UNSET
        elif isinstance(self.recipient_emails, list):
            recipient_emails = self.recipient_emails

        else:
            recipient_emails = self.recipient_emails

        report_title: None | str | Unset
        if isinstance(self.report_title, Unset):
            report_title = UNSET
        else:
            report_title = self.report_title

        sections: list[str] | None | Unset
        if isinstance(self.sections, Unset):
            sections = UNSET
        elif isinstance(self.sections, list):
            sections = self.sections

        else:
            sections = self.sections

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if format_ is not UNSET:
            field_dict["format"] = format_
        if interval_minutes is not UNSET:
            field_dict["interval_minutes"] = interval_minutes
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
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

        def _parse_domain_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        def _parse_format_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        format_ = _parse_format_(d.pop("format", UNSET))

        def _parse_interval_minutes(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        interval_minutes = _parse_interval_minutes(d.pop("interval_minutes", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_recipient_emails(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                recipient_emails_type_0 = cast(list[str], data)

                return recipient_emails_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        recipient_emails = _parse_recipient_emails(d.pop("recipient_emails", UNSET))

        def _parse_report_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        report_title = _parse_report_title(d.pop("report_title", UNSET))

        def _parse_sections(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sections_type_0 = cast(list[str], data)

                return sections_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        sections = _parse_sections(d.pop("sections", UNSET))

        scheduled_report_update = cls(
            domain_id=domain_id,
            format_=format_,
            interval_minutes=interval_minutes,
            is_active=is_active,
            name=name,
            recipient_emails=recipient_emails,
            report_title=report_title,
            sections=sections,
        )

        scheduled_report_update.additional_properties = d
        return scheduled_report_update

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
