from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CoauthorBackfillResponse")


@_attrs_define
class CoauthorBackfillResponse:
    """Counters returned by the CO_AUTHOR edge backfill.

    Attributes:
        edges_generated (int): Edges created (or estimated in dry-run).
        errors (int): Per-entity failures (rolled back individually).
        mode (str): 'dry-run' or 'applied'
        reset (bool): Whether existing CO_AUTHOR rows were wiped.
        scanned (int): Total entities visited under the filter.
        with_authors (int): Entities with at least 2 authors.
    """

    edges_generated: int
    errors: int
    mode: str
    reset: bool
    scanned: int
    with_authors: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        edges_generated = self.edges_generated

        errors = self.errors

        mode = self.mode

        reset = self.reset

        scanned = self.scanned

        with_authors = self.with_authors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "edges_generated": edges_generated,
                "errors": errors,
                "mode": mode,
                "reset": reset,
                "scanned": scanned,
                "with_authors": with_authors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        edges_generated = d.pop("edges_generated")

        errors = d.pop("errors")

        mode = d.pop("mode")

        reset = d.pop("reset")

        scanned = d.pop("scanned")

        with_authors = d.pop("with_authors")

        coauthor_backfill_response = cls(
            edges_generated=edges_generated,
            errors=errors,
            mode=mode,
            reset=reset,
            scanned=scanned,
            with_authors=with_authors,
        )

        coauthor_backfill_response.additional_properties = d
        return coauthor_backfill_response

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
