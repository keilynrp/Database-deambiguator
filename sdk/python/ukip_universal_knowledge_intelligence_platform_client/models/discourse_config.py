from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authority_sources import AuthoritySources
    from ..models.communication_channels import CommunicationChannels
    from ..models.health_metric_def import HealthMetricDef
    from ..models.validation_practice import ValidationPractice


T = TypeVar("T", bound="DiscourseConfig")


@_attrs_define
class DiscourseConfig:
    """
    Attributes:
        authority_sources (AuthoritySources | None | Unset):
        communication_channels (CommunicationChannels | None | Unset):
        health_metrics (list[HealthMetricDef] | Unset):
        validation_practices (list[ValidationPractice] | Unset):
    """

    authority_sources: AuthoritySources | None | Unset = UNSET
    communication_channels: CommunicationChannels | None | Unset = UNSET
    health_metrics: list[HealthMetricDef] | Unset = UNSET
    validation_practices: list[ValidationPractice] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.authority_sources import AuthoritySources
        from ..models.communication_channels import CommunicationChannels

        authority_sources: dict[str, Any] | None | Unset
        if isinstance(self.authority_sources, Unset):
            authority_sources = UNSET
        elif isinstance(self.authority_sources, AuthoritySources):
            authority_sources = self.authority_sources.to_dict()
        else:
            authority_sources = self.authority_sources

        communication_channels: dict[str, Any] | None | Unset
        if isinstance(self.communication_channels, Unset):
            communication_channels = UNSET
        elif isinstance(self.communication_channels, CommunicationChannels):
            communication_channels = self.communication_channels.to_dict()
        else:
            communication_channels = self.communication_channels

        health_metrics: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.health_metrics, Unset):
            health_metrics = []
            for health_metrics_item_data in self.health_metrics:
                health_metrics_item = health_metrics_item_data.to_dict()
                health_metrics.append(health_metrics_item)

        validation_practices: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.validation_practices, Unset):
            validation_practices = []
            for validation_practices_item_data in self.validation_practices:
                validation_practices_item = validation_practices_item_data.to_dict()
                validation_practices.append(validation_practices_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if authority_sources is not UNSET:
            field_dict["authority_sources"] = authority_sources
        if communication_channels is not UNSET:
            field_dict["communication_channels"] = communication_channels
        if health_metrics is not UNSET:
            field_dict["health_metrics"] = health_metrics
        if validation_practices is not UNSET:
            field_dict["validation_practices"] = validation_practices

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.authority_sources import AuthoritySources
        from ..models.communication_channels import CommunicationChannels
        from ..models.health_metric_def import HealthMetricDef
        from ..models.validation_practice import ValidationPractice

        d = dict(src_dict)

        def _parse_authority_sources(data: object) -> AuthoritySources | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                authority_sources_type_0 = AuthoritySources.from_dict(data)

                return authority_sources_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AuthoritySources | None | Unset, data)

        authority_sources = _parse_authority_sources(d.pop("authority_sources", UNSET))

        def _parse_communication_channels(data: object) -> CommunicationChannels | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                communication_channels_type_0 = CommunicationChannels.from_dict(data)

                return communication_channels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CommunicationChannels | None | Unset, data)

        communication_channels = _parse_communication_channels(d.pop("communication_channels", UNSET))

        _health_metrics = d.pop("health_metrics", UNSET)
        health_metrics: list[HealthMetricDef] | Unset = UNSET
        if _health_metrics is not UNSET:
            health_metrics = []
            for health_metrics_item_data in _health_metrics:
                health_metrics_item = HealthMetricDef.from_dict(health_metrics_item_data)

                health_metrics.append(health_metrics_item)

        _validation_practices = d.pop("validation_practices", UNSET)
        validation_practices: list[ValidationPractice] | Unset = UNSET
        if _validation_practices is not UNSET:
            validation_practices = []
            for validation_practices_item_data in _validation_practices:
                validation_practices_item = ValidationPractice.from_dict(validation_practices_item_data)

                validation_practices.append(validation_practices_item)

        discourse_config = cls(
            authority_sources=authority_sources,
            communication_channels=communication_channels,
            health_metrics=health_metrics,
            validation_practices=validation_practices,
        )

        discourse_config.additional_properties = d
        return discourse_config

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
