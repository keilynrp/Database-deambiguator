from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adapter_config import AdapterConfig


T = TypeVar("T", bound="DoiBatchRequest")


@_attrs_define
class DoiBatchRequest:
    """
    Attributes:
        dois (list[str]):
        config (AdapterConfig | Unset): Typed config for scientific adapters — only known keys allowed.
        source (str | Unset):  Default: 'crossref'.
    """

    dois: list[str]
    config: AdapterConfig | Unset = UNSET
    source: str | Unset = "crossref"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        dois = self.dois

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "dois": dois,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adapter_config import AdapterConfig

        d = dict(src_dict)
        dois = cast(list[str], d.pop("dois"))

        _config = d.pop("config", UNSET)
        config: AdapterConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = AdapterConfig.from_dict(_config)

        source = d.pop("source", UNSET)

        doi_batch_request = cls(
            dois=dois,
            config=config,
            source=source,
        )

        doi_batch_request.additional_properties = d
        return doi_batch_request

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
