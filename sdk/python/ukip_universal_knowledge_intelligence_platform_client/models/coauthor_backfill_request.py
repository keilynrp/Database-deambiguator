from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from ..types import UNSET, Unset

T = TypeVar("T", bound="CoauthorBackfillRequest")


@_attrs_define
class CoauthorBackfillRequest:
    """Inputs for the CO_AUTHOR edge backfill.

    Attributes:
        domain (None | str | Unset): Restrict to a single domain_id. None = all domains.
        dry_run (bool | Unset): If true, count entities + estimated edges without writing. Defaults to false because
            this fix is the only way to populate the coauthorship graph for legacy data. Default: False.
        reset (bool | Unset): Delete existing CO_AUTHOR rows before backfilling. Use only when you want a clean audit;
            the script is otherwise idempotent. Default: False.
    """

    domain: None | str | Unset = UNSET
    dry_run: bool | Unset = False
    reset: bool | Unset = False

    def to_dict(self) -> dict[str, Any]:
        domain: None | str | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        else:
            domain = self.domain

        dry_run = self.dry_run

        reset = self.reset

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if domain is not UNSET:
            field_dict["domain"] = domain
        if dry_run is not UNSET:
            field_dict["dry_run"] = dry_run
        if reset is not UNSET:
            field_dict["reset"] = reset

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_domain(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        dry_run = d.pop("dry_run", UNSET)

        reset = d.pop("reset", UNSET)

        coauthor_backfill_request = cls(
            domain=domain,
            dry_run=dry_run,
            reset=reset,
        )

        return coauthor_backfill_request
