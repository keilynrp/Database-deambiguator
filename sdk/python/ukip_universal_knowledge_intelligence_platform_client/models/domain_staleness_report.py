from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain_enrichment_policy_schema import DomainEnrichmentPolicySchema
    from ..models.enrichment_scheduler_run_schema import EnrichmentSchedulerRunSchema


T = TypeVar("T", bound="DomainStalenessReport")


@_attrs_define
class DomainStalenessReport:
    """Per-domain staleness report returned by GET /enrichment/schedule/{domain_id}.

    Attributes:
        current_enrichment_pct (float):
        domain_id (str):
        enriched_entities (int):
        is_stale (bool):
        stale_entities (int):
        total_entities (int):
        last_run (EnrichmentSchedulerRunSchema | None | Unset):
        policy (DomainEnrichmentPolicySchema | None | Unset):
    """

    current_enrichment_pct: float
    domain_id: str
    enriched_entities: int
    is_stale: bool
    stale_entities: int
    total_entities: int
    last_run: EnrichmentSchedulerRunSchema | None | Unset = UNSET
    policy: DomainEnrichmentPolicySchema | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.domain_enrichment_policy_schema import DomainEnrichmentPolicySchema
        from ..models.enrichment_scheduler_run_schema import EnrichmentSchedulerRunSchema

        current_enrichment_pct = self.current_enrichment_pct

        domain_id = self.domain_id

        enriched_entities = self.enriched_entities

        is_stale = self.is_stale

        stale_entities = self.stale_entities

        total_entities = self.total_entities

        last_run: dict[str, Any] | None | Unset
        if isinstance(self.last_run, Unset):
            last_run = UNSET
        elif isinstance(self.last_run, EnrichmentSchedulerRunSchema):
            last_run = self.last_run.to_dict()
        else:
            last_run = self.last_run

        policy: dict[str, Any] | None | Unset
        if isinstance(self.policy, Unset):
            policy = UNSET
        elif isinstance(self.policy, DomainEnrichmentPolicySchema):
            policy = self.policy.to_dict()
        else:
            policy = self.policy

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "current_enrichment_pct": current_enrichment_pct,
                "domain_id": domain_id,
                "enriched_entities": enriched_entities,
                "is_stale": is_stale,
                "stale_entities": stale_entities,
                "total_entities": total_entities,
            }
        )
        if last_run is not UNSET:
            field_dict["last_run"] = last_run
        if policy is not UNSET:
            field_dict["policy"] = policy

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.domain_enrichment_policy_schema import DomainEnrichmentPolicySchema
        from ..models.enrichment_scheduler_run_schema import EnrichmentSchedulerRunSchema

        d = dict(src_dict)
        current_enrichment_pct = d.pop("current_enrichment_pct")

        domain_id = d.pop("domain_id")

        enriched_entities = d.pop("enriched_entities")

        is_stale = d.pop("is_stale")

        stale_entities = d.pop("stale_entities")

        total_entities = d.pop("total_entities")

        def _parse_last_run(data: object) -> EnrichmentSchedulerRunSchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                last_run_type_0 = EnrichmentSchedulerRunSchema.from_dict(data)

                return last_run_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EnrichmentSchedulerRunSchema | None | Unset, data)

        last_run = _parse_last_run(d.pop("last_run", UNSET))

        def _parse_policy(data: object) -> DomainEnrichmentPolicySchema | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                policy_type_0 = DomainEnrichmentPolicySchema.from_dict(data)

                return policy_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DomainEnrichmentPolicySchema | None | Unset, data)

        policy = _parse_policy(d.pop("policy", UNSET))

        domain_staleness_report = cls(
            current_enrichment_pct=current_enrichment_pct,
            domain_id=domain_id,
            enriched_entities=enriched_entities,
            is_stale=is_stale,
            stale_entities=stale_entities,
            total_entities=total_entities,
            last_run=last_run,
            policy=policy,
        )

        domain_staleness_report.additional_properties = d
        return domain_staleness_report

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
