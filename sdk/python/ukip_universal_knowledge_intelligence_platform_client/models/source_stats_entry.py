from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.source_stats_entry_failure_reasons import SourceStatsEntryFailureReasons


T = TypeVar("T", bound="SourceStatsEntry")


@_attrs_define
class SourceStatsEntry:
    """Per-source enrichment outcome stats.

    Attributes:
        enriched (int):
        enrichment_source (None | str):
        failed (int):
        failure_reasons (SourceStatsEntryFailureReasons):
        total (int):
    """

    enriched: int
    enrichment_source: None | str
    failed: int
    failure_reasons: SourceStatsEntryFailureReasons
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enriched = self.enriched

        enrichment_source: None | str
        enrichment_source = self.enrichment_source

        failed = self.failed

        failure_reasons = self.failure_reasons.to_dict()

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "enriched": enriched,
                "enrichment_source": enrichment_source,
                "failed": failed,
                "failure_reasons": failure_reasons,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source_stats_entry_failure_reasons import SourceStatsEntryFailureReasons

        d = dict(src_dict)
        enriched = d.pop("enriched")

        def _parse_enrichment_source(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        enrichment_source = _parse_enrichment_source(d.pop("enrichment_source"))

        failed = d.pop("failed")

        failure_reasons = SourceStatsEntryFailureReasons.from_dict(d.pop("failure_reasons"))

        total = d.pop("total")

        source_stats_entry = cls(
            enriched=enriched,
            enrichment_source=enrichment_source,
            failed=failed,
            failure_reasons=failure_reasons,
            total=total,
        )

        source_stats_entry.additional_properties = d
        return source_stats_entry

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
