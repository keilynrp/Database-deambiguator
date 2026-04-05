"use client";

import { useState } from "react";

import {
  ACTION_TYPES,
  CONDITION_TYPES,
  TRIGGER_LABELS,
  type Action,
  type ActionType,
  type Condition,
  type ConditionType,
  type TriggerType,
  type Workflow,
  emptyAction,
  emptyCondition,
} from "./workflowTypes";

function ConditionEditor({
  condition,
  index,
  onChange,
  onRemove,
}: {
  condition: Condition;
  index: number;
  onChange: (i: number, c: Condition) => void;
  onRemove: (i: number) => void;
}) {
  return (
    <div className="flex items-start gap-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="grid flex-1 grid-cols-3 gap-2">
        <select
          value={condition.type}
          onChange={(e) => onChange(index, { ...condition, type: e.target.value as ConditionType })}
          className="rounded border border-slate-300 bg-white px-2 py-1.5 text-sm"
        >
          {CONDITION_TYPES.map((conditionType) => (
            <option key={conditionType.value} value={conditionType.value}>
              {conditionType.label}
            </option>
          ))}
        </select>
        <input
          placeholder="field name"
          value={condition.field}
          onChange={(e) => onChange(index, { ...condition, field: e.target.value })}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm"
          disabled={condition.type === "enrichment_status_is"}
        />
        <input
          placeholder="value"
          value={condition.value}
          onChange={(e) => onChange(index, { ...condition, value: e.target.value })}
          className="rounded border border-slate-300 px-2 py-1.5 text-sm"
          disabled={condition.type === "field_empty"}
        />
      </div>
      <button
        type="button"
        onClick={() => onRemove(index)}
        className="mt-1 text-slate-400 hover:text-rose-500"
        title="Remove condition"
      >
        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

function ActionEditor({
  action,
  index,
  onChange,
  onRemove,
}: {
  action: Action;
  index: number;
  onChange: (i: number, a: Action) => void;
  onRemove: (i: number) => void;
}) {
  const updateConfig = (key: string, value: unknown) =>
    onChange(index, { ...action, config: { ...action.config, [key]: value } });

  return (
    <div className="space-y-2 rounded-lg border border-slate-200 bg-slate-50 p-3">
      <div className="flex items-center gap-2">
        <select
          value={action.type}
          onChange={(e) => onChange(index, { type: e.target.value as ActionType, config: {} })}
          className="flex-1 rounded border border-slate-300 bg-white px-2 py-1.5 text-sm"
        >
          {ACTION_TYPES.map((actionType) => (
            <option key={actionType.value} value={actionType.value}>
              {actionType.label} - {actionType.description}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => onRemove(index)}
          className="text-slate-400 hover:text-rose-500"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {action.type === "send_webhook" && (
        <input
          placeholder="Webhook URL (https://...)"
          value={(action.config.url as string) || ""}
          onChange={(e) => updateConfig("url", e.target.value)}
          className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
        />
      )}
      {action.type === "tag_entity" && (
        <input
          placeholder="Tag to append (e.g. auto-reviewed)"
          value={(action.config.tag as string) || ""}
          onChange={(e) => updateConfig("tag", e.target.value)}
          className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
        />
      )}
      {action.type === "send_alert" && (
        <div className="grid grid-cols-2 gap-2">
          <input
            placeholder="Alert Channel ID"
            type="number"
            value={(action.config.channel_id as number) || ""}
            onChange={(e) => updateConfig("channel_id", parseInt(e.target.value, 10))}
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
          />
          <input
            placeholder="Message (optional)"
            value={(action.config.message as string) || ""}
            onChange={(e) => updateConfig("message", e.target.value)}
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
          />
        </div>
      )}
    </div>
  );
}

export function WorkflowForm({
  initial,
  onSave,
  onCancel,
}: {
  initial?: Partial<Workflow>;
  onSave: (data: Partial<Workflow>) => void;
  onCancel: () => void;
}) {
  const [name, setName] = useState(initial?.name ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [isActive, setIsActive] = useState(initial?.is_active ?? true);
  const [trigger, setTrigger] = useState<TriggerType>(initial?.trigger_type ?? "manual");
  const [conditions, setConditions] = useState<Condition[]>(initial?.conditions ?? []);
  const [actions, setActions] = useState<Action[]>(initial?.actions ?? [emptyAction()]);

  const updateCondition = (i: number, condition: Condition) =>
    setConditions((currentConditions) =>
      currentConditions.map((item, index) => (index === i ? condition : item)),
    );
  const removeCondition = (i: number) =>
    setConditions((currentConditions) => currentConditions.filter((_, index) => index !== i));
  const updateAction = (i: number, updatedAction: Action) =>
    setActions((currentActions) =>
      currentActions.map((item, index) => (index === i ? updatedAction : item)),
    );
  const removeAction = (i: number) =>
    setActions((currentActions) => currentActions.filter((_, index) => index !== i));

  const handleSubmit = () => {
    if (!name.trim()) {
      return;
    }
    onSave({
      name,
      description,
      is_active: isActive,
      trigger_type: trigger,
      conditions,
      actions,
    });
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Name *</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="My Workflow"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Trigger</label>
          <select
            value={trigger}
            onChange={(e) => setTrigger(e.target.value as TriggerType)}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
          >
            {Object.entries(TRIGGER_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Description</label>
          <input
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Optional description"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
          />
        </div>
        <div className="flex items-end gap-3">
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
              className="h-4 w-4 rounded accent-violet-600"
            />
            Active
          </label>
        </div>
      </div>

      <div>
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">
            Conditions{" "}
            <span className="font-normal text-slate-400">(all must match - leave empty to always run)</span>
          </h3>
          <button
            type="button"
            onClick={() => setConditions((currentConditions) => [...currentConditions, emptyCondition()])}
            className="text-xs font-medium text-violet-600 hover:text-violet-800"
          >
            + Add condition
          </button>
        </div>
        <div className="space-y-2">
          {conditions.length === 0 && (
            <p className="py-2 text-sm italic text-slate-400">No conditions - workflow always runs.</p>
          )}
          {conditions.map((condition, index) => (
            <ConditionEditor
              key={index}
              condition={condition}
              index={index}
              onChange={updateCondition}
              onRemove={removeCondition}
            />
          ))}
        </div>
      </div>

      <div>
        <div className="mb-2 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">Actions</h3>
          <button
            type="button"
            onClick={() => setActions((currentActions) => [...currentActions, emptyAction()])}
            className="text-xs font-medium text-violet-600 hover:text-violet-800"
          >
            + Add action
          </button>
        </div>
        <div className="space-y-2">
          {actions.map((action, index) => (
            <ActionEditor
              key={index}
              action={action}
              index={index}
              onChange={updateAction}
              onRemove={removeAction}
            />
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-3 border-t border-slate-200 pt-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm text-slate-600 hover:text-slate-900"
        >
          Cancel
        </button>
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!name.trim()}
          className="rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          Save Workflow
        </button>
      </div>
    </div>
  );
}
