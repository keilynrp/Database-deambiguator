from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.org_update_benchmark_profile_overrides_type_0 import OrgUpdateBenchmarkProfileOverridesType0


T = TypeVar("T", bound="OrgUpdate")


@_attrs_define
class OrgUpdate:
    """
    Attributes:
        benchmark_profile_id (None | str | Unset):
        benchmark_profile_overrides (None | OrgUpdateBenchmarkProfileOverridesType0 | Unset):
        description (None | str | Unset):
        name (None | str | Unset):
        plan (None | str | Unset):
    """

    benchmark_profile_id: None | str | Unset = UNSET
    benchmark_profile_overrides: None | OrgUpdateBenchmarkProfileOverridesType0 | Unset = UNSET
    description: None | str | Unset = UNSET
    name: None | str | Unset = UNSET
    plan: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.org_update_benchmark_profile_overrides_type_0 import OrgUpdateBenchmarkProfileOverridesType0

        benchmark_profile_id: None | str | Unset
        if isinstance(self.benchmark_profile_id, Unset):
            benchmark_profile_id = UNSET
        else:
            benchmark_profile_id = self.benchmark_profile_id

        benchmark_profile_overrides: dict[str, Any] | None | Unset
        if isinstance(self.benchmark_profile_overrides, Unset):
            benchmark_profile_overrides = UNSET
        elif isinstance(self.benchmark_profile_overrides, OrgUpdateBenchmarkProfileOverridesType0):
            benchmark_profile_overrides = self.benchmark_profile_overrides.to_dict()
        else:
            benchmark_profile_overrides = self.benchmark_profile_overrides

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        plan: None | str | Unset
        if isinstance(self.plan, Unset):
            plan = UNSET
        else:
            plan = self.plan

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if benchmark_profile_id is not UNSET:
            field_dict["benchmark_profile_id"] = benchmark_profile_id
        if benchmark_profile_overrides is not UNSET:
            field_dict["benchmark_profile_overrides"] = benchmark_profile_overrides
        if description is not UNSET:
            field_dict["description"] = description
        if name is not UNSET:
            field_dict["name"] = name
        if plan is not UNSET:
            field_dict["plan"] = plan

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.org_update_benchmark_profile_overrides_type_0 import OrgUpdateBenchmarkProfileOverridesType0

        d = dict(src_dict)

        def _parse_benchmark_profile_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        benchmark_profile_id = _parse_benchmark_profile_id(d.pop("benchmark_profile_id", UNSET))

        def _parse_benchmark_profile_overrides(data: object) -> None | OrgUpdateBenchmarkProfileOverridesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                benchmark_profile_overrides_type_0 = OrgUpdateBenchmarkProfileOverridesType0.from_dict(data)

                return benchmark_profile_overrides_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OrgUpdateBenchmarkProfileOverridesType0 | Unset, data)

        benchmark_profile_overrides = _parse_benchmark_profile_overrides(d.pop("benchmark_profile_overrides", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_plan(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        plan = _parse_plan(d.pop("plan", UNSET))

        org_update = cls(
            benchmark_profile_id=benchmark_profile_id,
            benchmark_profile_overrides=benchmark_profile_overrides,
            description=description,
            name=name,
            plan=plan,
        )

        org_update.additional_properties = d
        return org_update

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
