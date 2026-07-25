from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AssistantActionAuditPayload")


@_attrs_define
class AssistantActionAuditPayload:
    """
    Attributes:
        action_id (str):
        label (str):
        api_path (None | str | Unset):
        detail (None | str | Unset):
        domain_id (None | str | Unset):
        href (None | str | Unset):
        kind (None | str | Unset):
        method (None | str | Unset):
        module_label (None | str | Unset):
        route (None | str | Unset):
        status (str | Unset):  Default: 'started'.
        status_code (int | None | Unset):
    """

    action_id: str
    label: str
    api_path: None | str | Unset = UNSET
    detail: None | str | Unset = UNSET
    domain_id: None | str | Unset = UNSET
    href: None | str | Unset = UNSET
    kind: None | str | Unset = UNSET
    method: None | str | Unset = UNSET
    module_label: None | str | Unset = UNSET
    route: None | str | Unset = UNSET
    status: str | Unset = "started"
    status_code: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action_id = self.action_id

        label = self.label

        api_path: None | str | Unset
        if isinstance(self.api_path, Unset):
            api_path = UNSET
        else:
            api_path = self.api_path

        detail: None | str | Unset
        if isinstance(self.detail, Unset):
            detail = UNSET
        else:
            detail = self.detail

        domain_id: None | str | Unset
        if isinstance(self.domain_id, Unset):
            domain_id = UNSET
        else:
            domain_id = self.domain_id

        href: None | str | Unset
        if isinstance(self.href, Unset):
            href = UNSET
        else:
            href = self.href

        kind: None | str | Unset
        if isinstance(self.kind, Unset):
            kind = UNSET
        else:
            kind = self.kind

        method: None | str | Unset
        if isinstance(self.method, Unset):
            method = UNSET
        else:
            method = self.method

        module_label: None | str | Unset
        if isinstance(self.module_label, Unset):
            module_label = UNSET
        else:
            module_label = self.module_label

        route: None | str | Unset
        if isinstance(self.route, Unset):
            route = UNSET
        else:
            route = self.route

        status = self.status

        status_code: int | None | Unset
        if isinstance(self.status_code, Unset):
            status_code = UNSET
        else:
            status_code = self.status_code

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action_id": action_id,
                "label": label,
            }
        )
        if api_path is not UNSET:
            field_dict["api_path"] = api_path
        if detail is not UNSET:
            field_dict["detail"] = detail
        if domain_id is not UNSET:
            field_dict["domain_id"] = domain_id
        if href is not UNSET:
            field_dict["href"] = href
        if kind is not UNSET:
            field_dict["kind"] = kind
        if method is not UNSET:
            field_dict["method"] = method
        if module_label is not UNSET:
            field_dict["module_label"] = module_label
        if route is not UNSET:
            field_dict["route"] = route
        if status is not UNSET:
            field_dict["status"] = status
        if status_code is not UNSET:
            field_dict["status_code"] = status_code

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        action_id = d.pop("action_id")

        label = d.pop("label")

        def _parse_api_path(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        api_path = _parse_api_path(d.pop("api_path", UNSET))

        def _parse_detail(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        detail = _parse_detail(d.pop("detail", UNSET))

        def _parse_domain_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        domain_id = _parse_domain_id(d.pop("domain_id", UNSET))

        def _parse_href(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        href = _parse_href(d.pop("href", UNSET))

        def _parse_kind(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        kind = _parse_kind(d.pop("kind", UNSET))

        def _parse_method(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        method = _parse_method(d.pop("method", UNSET))

        def _parse_module_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        module_label = _parse_module_label(d.pop("module_label", UNSET))

        def _parse_route(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        route = _parse_route(d.pop("route", UNSET))

        status = d.pop("status", UNSET)

        def _parse_status_code(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        status_code = _parse_status_code(d.pop("status_code", UNSET))

        assistant_action_audit_payload = cls(
            action_id=action_id,
            label=label,
            api_path=api_path,
            detail=detail,
            domain_id=domain_id,
            href=href,
            kind=kind,
            method=method,
            module_label=module_label,
            route=route,
            status=status,
            status_code=status_code,
        )

        assistant_action_audit_payload.additional_properties = d
        return assistant_action_audit_payload

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
