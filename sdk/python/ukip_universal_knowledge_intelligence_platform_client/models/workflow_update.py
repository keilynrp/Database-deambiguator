from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.action_schema import ActionSchema
    from ..models.condition_schema import ConditionSchema
    from ..models.workflow_update_trigger_config_type_0 import WorkflowUpdateTriggerConfigType0


T = TypeVar("T", bound="WorkflowUpdate")


@_attrs_define
class WorkflowUpdate:
    """
    Attributes:
        actions (list[ActionSchema] | None | Unset):
        conditions (list[ConditionSchema] | None | Unset):
        description (None | str | Unset):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        trigger_config (None | Unset | WorkflowUpdateTriggerConfigType0):
        trigger_type (None | str | Unset):
    """

    actions: list[ActionSchema] | None | Unset = UNSET
    conditions: list[ConditionSchema] | None | Unset = UNSET
    description: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    trigger_config: None | Unset | WorkflowUpdateTriggerConfigType0 = UNSET
    trigger_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.workflow_update_trigger_config_type_0 import WorkflowUpdateTriggerConfigType0

        actions: list[dict[str, Any]] | None | Unset
        if isinstance(self.actions, Unset):
            actions = UNSET
        elif isinstance(self.actions, list):
            actions = []
            for actions_type_0_item_data in self.actions:
                actions_type_0_item = actions_type_0_item_data.to_dict()
                actions.append(actions_type_0_item)

        else:
            actions = self.actions

        conditions: list[dict[str, Any]] | None | Unset
        if isinstance(self.conditions, Unset):
            conditions = UNSET
        elif isinstance(self.conditions, list):
            conditions = []
            for conditions_type_0_item_data in self.conditions:
                conditions_type_0_item = conditions_type_0_item_data.to_dict()
                conditions.append(conditions_type_0_item)

        else:
            conditions = self.conditions

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        trigger_config: dict[str, Any] | None | Unset
        if isinstance(self.trigger_config, Unset):
            trigger_config = UNSET
        elif isinstance(self.trigger_config, WorkflowUpdateTriggerConfigType0):
            trigger_config = self.trigger_config.to_dict()
        else:
            trigger_config = self.trigger_config

        trigger_type: None | str | Unset
        if isinstance(self.trigger_type, Unset):
            trigger_type = UNSET
        else:
            trigger_type = self.trigger_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if actions is not UNSET:
            field_dict["actions"] = actions
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if trigger_config is not UNSET:
            field_dict["trigger_config"] = trigger_config
        if trigger_type is not UNSET:
            field_dict["trigger_type"] = trigger_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_schema import ActionSchema
        from ..models.condition_schema import ConditionSchema
        from ..models.workflow_update_trigger_config_type_0 import WorkflowUpdateTriggerConfigType0

        d = dict(src_dict)

        def _parse_actions(data: object) -> list[ActionSchema] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                actions_type_0 = []
                _actions_type_0 = data
                for actions_type_0_item_data in _actions_type_0:
                    actions_type_0_item = ActionSchema.from_dict(actions_type_0_item_data)

                    actions_type_0.append(actions_type_0_item)

                return actions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ActionSchema] | None | Unset, data)

        actions = _parse_actions(d.pop("actions", UNSET))

        def _parse_conditions(data: object) -> list[ConditionSchema] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                conditions_type_0 = []
                _conditions_type_0 = data
                for conditions_type_0_item_data in _conditions_type_0:
                    conditions_type_0_item = ConditionSchema.from_dict(conditions_type_0_item_data)

                    conditions_type_0.append(conditions_type_0_item)

                return conditions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ConditionSchema] | None | Unset, data)

        conditions = _parse_conditions(d.pop("conditions", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_trigger_config(data: object) -> None | Unset | WorkflowUpdateTriggerConfigType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                trigger_config_type_0 = WorkflowUpdateTriggerConfigType0.from_dict(data)

                return trigger_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | WorkflowUpdateTriggerConfigType0, data)

        trigger_config = _parse_trigger_config(d.pop("trigger_config", UNSET))

        def _parse_trigger_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        trigger_type = _parse_trigger_type(d.pop("trigger_type", UNSET))

        workflow_update = cls(
            actions=actions,
            conditions=conditions,
            description=description,
            is_active=is_active,
            name=name,
            trigger_config=trigger_config,
            trigger_type=trigger_type,
        )

        workflow_update.additional_properties = d
        return workflow_update

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
