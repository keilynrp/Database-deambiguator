from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adapter_config import AdapterConfig


T = TypeVar("T", bound="SearchRequest")


@_attrs_define
class SearchRequest:
    """
    Attributes:
        query (str):
        source (str):
        config (AdapterConfig | Unset): Typed config for scientific adapters — only known keys allowed.
        max_results (int | Unset):  Default: 20.
        use_engine (bool | Unset): Opt-in to Rust engine delegation Default: False.
    """

    query: str
    source: str
    config: AdapterConfig | Unset = UNSET
    max_results: int | Unset = 20
    use_engine: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        source = self.source

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        max_results = self.max_results

        use_engine = self.use_engine

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
                "source": source,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if max_results is not UNSET:
            field_dict["max_results"] = max_results
        if use_engine is not UNSET:
            field_dict["use_engine"] = use_engine

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adapter_config import AdapterConfig

        d = dict(src_dict)
        query = d.pop("query")

        source = d.pop("source")

        _config = d.pop("config", UNSET)
        config: AdapterConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = AdapterConfig.from_dict(_config)

        max_results = d.pop("max_results", UNSET)

        use_engine = d.pop("use_engine", UNSET)

        search_request = cls(
            query=query,
            source=source,
            config=config,
            max_results=max_results,
            use_engine=use_engine,
        )

        search_request.additional_properties = d
        return search_request

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
