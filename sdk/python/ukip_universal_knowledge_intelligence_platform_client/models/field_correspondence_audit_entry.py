from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.field_correspondence_audit_entry_after_type_0 import FieldCorrespondenceAuditEntryAfterType0
    from ..models.field_correspondence_audit_entry_before_type_0 import FieldCorrespondenceAuditEntryBeforeType0


T = TypeVar("T", bound="FieldCorrespondenceAuditEntry")


@_attrs_define
class FieldCorrespondenceAuditEntry:
    """
    Attributes:
        action (str):
        id (int):
        after (FieldCorrespondenceAuditEntryAfterType0 | None | Unset):
        before (FieldCorrespondenceAuditEntryBeforeType0 | None | Unset):
        created_at (None | str | Unset):
        username (None | str | Unset):
    """

    action: str
    id: int
    after: FieldCorrespondenceAuditEntryAfterType0 | None | Unset = UNSET
    before: FieldCorrespondenceAuditEntryBeforeType0 | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    username: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.field_correspondence_audit_entry_after_type_0 import FieldCorrespondenceAuditEntryAfterType0
        from ..models.field_correspondence_audit_entry_before_type_0 import FieldCorrespondenceAuditEntryBeforeType0

        action = self.action

        id = self.id

        after: dict[str, Any] | None | Unset
        if isinstance(self.after, Unset):
            after = UNSET
        elif isinstance(self.after, FieldCorrespondenceAuditEntryAfterType0):
            after = self.after.to_dict()
        else:
            after = self.after

        before: dict[str, Any] | None | Unset
        if isinstance(self.before, Unset):
            before = UNSET
        elif isinstance(self.before, FieldCorrespondenceAuditEntryBeforeType0):
            before = self.before.to_dict()
        else:
            before = self.before

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        username: None | str | Unset
        if isinstance(self.username, Unset):
            username = UNSET
        else:
            username = self.username

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "id": id,
            }
        )
        if after is not UNSET:
            field_dict["after"] = after
        if before is not UNSET:
            field_dict["before"] = before
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if username is not UNSET:
            field_dict["username"] = username

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.field_correspondence_audit_entry_after_type_0 import FieldCorrespondenceAuditEntryAfterType0
        from ..models.field_correspondence_audit_entry_before_type_0 import FieldCorrespondenceAuditEntryBeforeType0

        d = dict(src_dict)
        action = d.pop("action")

        id = d.pop("id")

        def _parse_after(data: object) -> FieldCorrespondenceAuditEntryAfterType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                after_type_0 = FieldCorrespondenceAuditEntryAfterType0.from_dict(data)

                return after_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FieldCorrespondenceAuditEntryAfterType0 | None | Unset, data)

        after = _parse_after(d.pop("after", UNSET))

        def _parse_before(data: object) -> FieldCorrespondenceAuditEntryBeforeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                before_type_0 = FieldCorrespondenceAuditEntryBeforeType0.from_dict(data)

                return before_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FieldCorrespondenceAuditEntryBeforeType0 | None | Unset, data)

        before = _parse_before(d.pop("before", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_username(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        username = _parse_username(d.pop("username", UNSET))

        field_correspondence_audit_entry = cls(
            action=action,
            id=id,
            after=after,
            before=before,
            created_at=created_at,
            username=username,
        )

        field_correspondence_audit_entry.additional_properties = d
        return field_correspondence_audit_entry

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
