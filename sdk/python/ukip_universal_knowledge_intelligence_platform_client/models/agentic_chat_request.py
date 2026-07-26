from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.agentic_chat_request_mode import AgenticChatRequestMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="AgenticChatRequest")


@_attrs_define
class AgenticChatRequest:
    """
    Attributes:
        question (str):
        domain_id (str | Unset):  Default: 'default'.
        entity_id (int | None | Unset):
        import_batch_id (int | None | Unset):
        mode (AgenticChatRequestMode | Unset):  Default: AgenticChatRequestMode.AUTO.
        persist_trace (bool | Unset):  Default: True.
        portal_slug (None | str | Unset):
        provider (None | str | Unset):
        top_k (int | Unset):  Default: 6.
        use_tools (bool | Unset):  Default: True.
    """

    question: str
    domain_id: str | Unset = "default"
    entity_id: int | None | Unset = UNSET
    import_batch_id: int | None | Unset = UNSET
    mode: AgenticChatRequestMode | Unset = AgenticChatRequestMode.AUTO
    persist_trace: bool | Unset = True
    portal_slug: None | str | Unset = UNSET
    provider: None | str | Unset = UNSET
    top_k: int | Unset = 6
    use_tools: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        question = self.question

        domain_id = self.domain_id

        entity_id: int | None | Unset
        if isinstance(self.entity_id, Unset):
            entity_id = UNSET
        else:
            entity_id = self.entity_id

        import_batch_id: int | None | Unset
        if isinstance(self.import_batch_id, Unset):
            import_batch_id = UNSET
        else:
            import_batch_id = self.import_batch_id

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        persist_trace = self.persist_trace

        portal_slug: None | str | Unset
        if isinstance(self.portal_slug, Unset):
            portal_slug = UNSET
        else:
            portal_slug = self.portal_slug

        provider: None | str | Unset
        if isinstance(self.provider, Unset):
            provider = UNSET
        else:
            provider = self.provider

        top_k = self.top_k

        use_tools = self.use_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "question": question,
            }
        )
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if entity_id is not UNSET:
            field_dict["entity_id"] = entity_id
        if import_batch_id is not UNSET:
            field_dict["import_batch_id"] = import_batch_id
        if mode is not UNSET:
            field_dict["mode"] = mode
        if persist_trace is not UNSET:
            field_dict["persist_trace"] = persist_trace
        if portal_slug is not UNSET:
            field_dict["portal_slug"] = portal_slug
        if provider is not UNSET:
            field_dict["provider"] = provider
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if use_tools is not UNSET:
            field_dict["use_tools"] = use_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        question = d.pop("question")

        domain_id = d.pop("domain_id", UNSET)

        def _parse_entity_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        entity_id = _parse_entity_id(d.pop("entity_id", UNSET))

        def _parse_import_batch_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        import_batch_id = _parse_import_batch_id(d.pop("import_batch_id", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: AgenticChatRequestMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = AgenticChatRequestMode(_mode)

        persist_trace = d.pop("persist_trace", UNSET)

        def _parse_portal_slug(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        portal_slug = _parse_portal_slug(d.pop("portal_slug", UNSET))

        def _parse_provider(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        provider = _parse_provider(d.pop("provider", UNSET))

        top_k = d.pop("top_k", UNSET)

        use_tools = d.pop("use_tools", UNSET)

        agentic_chat_request = cls(
            question=question,
            domain_id=domain_id,
            entity_id=entity_id,
            import_batch_id=import_batch_id,
            mode=mode,
            persist_trace=persist_trace,
            portal_slug=portal_slug,
            provider=provider,
            top_k=top_k,
            use_tools=use_tools,
        )

        agentic_chat_request.additional_properties = d
        return agentic_chat_request

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
