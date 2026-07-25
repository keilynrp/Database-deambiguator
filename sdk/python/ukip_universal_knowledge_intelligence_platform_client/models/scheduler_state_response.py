from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SchedulerStateResponse")


@_attrs_define
class SchedulerStateResponse:
    """Global scheduler state returned by GET /enrichment/schedule.

    Attributes:
        domains_monitored (int):
        enabled (bool):
        interval_seconds (int):
        total_queued_last_run (int):
        last_run_at (datetime.datetime | None | Unset):
        next_run_at (datetime.datetime | None | Unset):
    """

    domains_monitored: int
    enabled: bool
    interval_seconds: int
    total_queued_last_run: int
    last_run_at: datetime.datetime | None | Unset = UNSET
    next_run_at: datetime.datetime | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domains_monitored = self.domains_monitored

        enabled = self.enabled

        interval_seconds = self.interval_seconds

        total_queued_last_run = self.total_queued_last_run

        last_run_at: None | str | Unset
        if isinstance(self.last_run_at, Unset):
            last_run_at = UNSET
        elif isinstance(self.last_run_at, datetime.datetime):
            last_run_at = self.last_run_at.isoformat()
        else:
            last_run_at = self.last_run_at

        next_run_at: None | str | Unset
        if isinstance(self.next_run_at, Unset):
            next_run_at = UNSET
        elif isinstance(self.next_run_at, datetime.datetime):
            next_run_at = self.next_run_at.isoformat()
        else:
            next_run_at = self.next_run_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domains_monitored": domains_monitored,
                "enabled": enabled,
                "interval_seconds": interval_seconds,
                "total_queued_last_run": total_queued_last_run,
            }
        )
        if last_run_at is not UNSET:
            field_dict["last_run_at"] = last_run_at
        if next_run_at is not UNSET:
            field_dict["next_run_at"] = next_run_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domains_monitored = d.pop("domains_monitored")

        enabled = d.pop("enabled")

        interval_seconds = d.pop("interval_seconds")

        total_queued_last_run = d.pop("total_queued_last_run")

        def _parse_last_run_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_run_at_type_0 = datetime.datetime.fromisoformat(data)

                return last_run_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_run_at = _parse_last_run_at(d.pop("last_run_at", UNSET))

        def _parse_next_run_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                next_run_at_type_0 = datetime.datetime.fromisoformat(data)

                return next_run_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        next_run_at = _parse_next_run_at(d.pop("next_run_at", UNSET))

        scheduler_state_response = cls(
            domains_monitored=domains_monitored,
            enabled=enabled,
            interval_seconds=interval_seconds,
            total_queued_last_run=total_queued_last_run,
            last_run_at=last_run_at,
            next_run_at=next_run_at,
        )

        scheduler_state_response.additional_properties = d
        return scheduler_state_response

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
