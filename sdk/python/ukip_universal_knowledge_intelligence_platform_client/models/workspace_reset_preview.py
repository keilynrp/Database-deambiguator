from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.workspace_reset_preview_counts import WorkspaceResetPreviewCounts


T = TypeVar("T", bound="WorkspaceResetPreview")


@_attrs_define
class WorkspaceResetPreview:
    """
    Attributes:
        counts (WorkspaceResetPreviewCounts):
        scope_label (str):
        scope_type (str):
        confirmation_text (str | Unset):  Default: 'RESET'.
        preserved (list[str] | Unset):
    """

    counts: WorkspaceResetPreviewCounts
    scope_label: str
    scope_type: str
    confirmation_text: str | Unset = "RESET"
    preserved: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        counts = self.counts.to_dict()

        scope_label = self.scope_label

        scope_type = self.scope_type

        confirmation_text = self.confirmation_text

        preserved: list[str] | Unset = UNSET
        if not isinstance(self.preserved, Unset):
            preserved = self.preserved

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "counts": counts,
                "scope_label": scope_label,
                "scope_type": scope_type,
            }
        )
        if confirmation_text is not UNSET:
            field_dict["confirmation_text"] = confirmation_text
        if preserved is not UNSET:
            field_dict["preserved"] = preserved

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workspace_reset_preview_counts import WorkspaceResetPreviewCounts

        d = dict(src_dict)
        counts = WorkspaceResetPreviewCounts.from_dict(d.pop("counts"))

        scope_label = d.pop("scope_label")

        scope_type = d.pop("scope_type")

        confirmation_text = d.pop("confirmation_text", UNSET)

        preserved = cast(list[str], d.pop("preserved", UNSET))

        workspace_reset_preview = cls(
            counts=counts,
            scope_label=scope_label,
            scope_type=scope_type,
            confirmation_text=confirmation_text,
            preserved=preserved,
        )

        workspace_reset_preview.additional_properties = d
        return workspace_reset_preview

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
