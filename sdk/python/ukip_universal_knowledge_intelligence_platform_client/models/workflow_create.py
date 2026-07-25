from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.action_schema import ActionSchema
    from ..models.condition_schema import ConditionSchema
    from ..models.workflow_create_trigger_config import WorkflowCreateTriggerConfig


T = TypeVar("T", bound="WorkflowCreate")


@_attrs_define
class WorkflowCreate:
    """
    Attributes:
        name (str):
        trigger_type (str):
        actions (list[ActionSchema] | Unset):
        conditions (list[ConditionSchema] | Unset):
        description (None | str | Unset):
        is_active (bool | Unset):  Default: True.
        trigger_config (WorkflowCreateTriggerConfig | Unset):
    """

    name: str
    trigger_type: str
    actions: list[ActionSchema] | Unset = UNSET
    conditions: list[ConditionSchema] | Unset = UNSET
    description: None | str | Unset = UNSET
    is_active: bool | Unset = True
    trigger_config: WorkflowCreateTriggerConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        trigger_type = self.trigger_type

        actions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.actions, Unset):
            actions = []
            for actions_item_data in self.actions:
                actions_item = actions_item_data.to_dict()
                actions.append(actions_item)

        conditions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.conditions, Unset):
            conditions = []
            for conditions_item_data in self.conditions:
                conditions_item = conditions_item_data.to_dict()
                conditions.append(conditions_item)

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_active = self.is_active

        trigger_config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.trigger_config, Unset):
            trigger_config = self.trigger_config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "trigger_type": trigger_type,
            }
        )
        if actions is not UNSET:
            field_dict["actions"] = actions
        if conditions is not UNSET:
            field_dict["conditions"] = conditions
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if trigger_config is not UNSET:
            field_dict["trigger_config"] = trigger_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.action_schema import ActionSchema
        from ..models.condition_schema import ConditionSchema
        from ..models.workflow_create_trigger_config import WorkflowCreateTriggerConfig

        d = dict(src_dict)
        name = d.pop("name")

        trigger_type = d.pop("trigger_type")

        _actions = d.pop("actions", UNSET)
        actions: list[ActionSchema] | Unset = UNSET
        if _actions is not UNSET:
            actions = []
            for actions_item_data in _actions:
                actions_item = ActionSchema.from_dict(actions_item_data)

                actions.append(actions_item)

        _conditions = d.pop("conditions", UNSET)
        conditions: list[ConditionSchema] | Unset = UNSET
        if _conditions is not UNSET:
            conditions = []
            for conditions_item_data in _conditions:
                conditions_item = ConditionSchema.from_dict(conditions_item_data)

                conditions.append(conditions_item)

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        is_active = d.pop("is_active", UNSET)

        _trigger_config = d.pop("trigger_config", UNSET)
        trigger_config: WorkflowCreateTriggerConfig | Unset
        if isinstance(_trigger_config, Unset):
            trigger_config = UNSET
        else:
            trigger_config = WorkflowCreateTriggerConfig.from_dict(_trigger_config)

        workflow_create = cls(
            name=name,
            trigger_type=trigger_type,
            actions=actions,
            conditions=conditions,
            description=description,
            is_active=is_active,
            trigger_config=trigger_config,
        )

        workflow_create.additional_properties = d
        return workflow_create

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
