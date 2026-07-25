from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RAGQueryPayload")


@_attrs_define
class RAGQueryPayload:
    """
    Attributes:
        question (str):
        domain_id (None | str | Unset):
        min_similarity (float | Unset):  Default: 0.35.
        session_id (int | None | Unset):
        top_k (int | Unset):  Default: 5.
        use_context (bool | Unset):  Default: False.
        use_tools (bool | Unset):  Default: False.
    """

    question: str
    domain_id: None | str | Unset = UNSET
    min_similarity: float | Unset = 0.35
    session_id: int | None | Unset = UNSET
    top_k: int | Unset = 5
    use_context: bool | Unset = False
    use_tools: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        question = self.question

        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        else:
            domain_id = self.domain_id

        min_similarity = self.min_similarity

        session_id: int | None | Unset
        if isinstance(self.session_id, Unset):
            session_id = UNSET
        else:
            session_id = self.session_id

        top_k = self.top_k

        use_context = self.use_context

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
        if min_similarity is not UNSET:
            field_dict["min_similarity"] = min_similarity
        if session_id is not UNSET:
            field_dict["session_id"] = session_id
        if top_k is not UNSET:
            field_dict["top_k"] = top_k
        if use_context is not UNSET:
            field_dict["use_context"] = use_context
        if use_tools is not UNSET:
            field_dict["use_tools"] = use_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        question = d.pop("question")

        def _parse_domain_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        min_similarity = d.pop("min_similarity", UNSET)

        def _parse_session_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        session_id = _parse_session_id(d.pop("session_id", UNSET))

        top_k = d.pop("top_k", UNSET)

        use_context = d.pop("use_context", UNSET)

        use_tools = d.pop("use_tools", UNSET)

        rag_query_payload = cls(
            question=question,
            domain_id=domain_id,
            min_similarity=min_similarity,
            session_id=session_id,
            top_k=top_k,
            use_context=use_context,
            use_tools=use_tools,
        )

        rag_query_payload.additional_properties = d
        return rag_query_payload

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
