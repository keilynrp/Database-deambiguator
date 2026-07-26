from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SingleEntityObservationInput")


@_attrs_define
class SingleEntityObservationInput:
    """
    Attributes:
        source_type (str):
        last_seen_at (None | str | Unset):
        mention_count (int | Unset):  Default: 1.
        snippet (None | str | Unset):
        title (None | str | Unset):
        url (None | str | Unset):
    """

    source_type: str
    last_seen_at: None | str | Unset = UNSET
    mention_count: int | Unset = 1
    snippet: None | str | Unset = UNSET
    title: None | str | Unset = UNSET
    url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        source_type = self.source_type

        last_seen_at: None | str | Unset
        if isinstance(self.last_seen_at, Unset):
            last_seen_at = UNSET
        else:
            last_seen_at = self.last_seen_at

        mention_count = self.mention_count

        snippet: None | str | Unset
        if isinstance(self.snippet, Unset):
            snippet = UNSET
        else:
            snippet = self.snippet

        title: None | str | Unset
        if isinstance(self.title, Unset):
            title = UNSET
        else:
            title = self.title

        url: None | str | Unset
        if isinstance(self.url, Unset):
            url = UNSET
        else:
            url = self.url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_type": source_type,
            }
        )
        if last_seen_at is not UNSET:
            field_dict["last_seen_at"] = last_seen_at
        if mention_count is not UNSET:
            field_dict["mention_count"] = mention_count
        if snippet is not UNSET:
            field_dict["snippet"] = snippet
        if title is not UNSET:
            field_dict["title"] = title
        if url is not UNSET:
            field_dict["url"] = url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        source_type = d.pop("source_type")

        def _parse_last_seen_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_seen_at = _parse_last_seen_at(d.pop("last_seen_at", UNSET))

        mention_count = d.pop("mention_count", UNSET)

        def _parse_snippet(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        snippet = _parse_snippet(d.pop("snippet", UNSET))

        def _parse_title(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        title = _parse_title(d.pop("title", UNSET))

        def _parse_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        url = _parse_url(d.pop("url", UNSET))

        single_entity_observation_input = cls(
            source_type=source_type,
            last_seen_at=last_seen_at,
            mention_count=mention_count,
            snippet=snippet,
            title=title,
            url=url,
        )

        single_entity_observation_input.additional_properties = d
        return single_entity_observation_input

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
