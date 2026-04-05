"use client";

export type TriggerType = "entity.created" | "entity.enriched" | "entity.flagged" | "manual";
export type ConditionType = "field_equals" | "field_contains" | "field_empty" | "enrichment_status_is";
export type ActionType = "send_webhook" | "tag_entity" | "send_alert" | "log_only";

export interface Condition {
  type: ConditionType;
  field: string;
  value: string;
}

export interface Action {
  type: ActionType;
  config: Record<string, unknown>;
}

export interface Workflow {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  trigger_type: TriggerType;
  conditions: Condition[];
  actions: Action[];
  run_count: number;
  last_run_at: string | null;
  last_run_status: string | null;
  created_at: string | null;
}

export interface WorkflowRun {
  id: number;
  workflow_id: number;
  status: string;
  trigger_data: Record<string, unknown>;
  steps_log: Array<{ action: string; result: Record<string, unknown> }>;
  error: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export const TRIGGER_LABELS: Record<TriggerType, string> = {
  "entity.created": "Entity Created",
  "entity.enriched": "Entity Enriched",
  "entity.flagged": "Entity Flagged",
  manual: "Manual",
};

export const TRIGGER_COLORS: Record<TriggerType, string> = {
  "entity.created": "bg-emerald-100 text-emerald-800",
  "entity.enriched": "bg-blue-100 text-blue-800",
  "entity.flagged": "bg-rose-100 text-rose-800",
  manual: "bg-violet-100 text-violet-800",
};

export const STATUS_COLORS: Record<string, string> = {
  success: "bg-emerald-100 text-emerald-700",
  error: "bg-rose-100 text-rose-700",
  skipped: "bg-amber-100 text-amber-700",
  running: "bg-blue-100 text-blue-700",
};

export const CONDITION_TYPES: Array<{ value: ConditionType; label: string }> = [
  { value: "field_equals", label: "Field equals" },
  { value: "field_contains", label: "Field contains" },
  { value: "field_empty", label: "Field is empty" },
  { value: "enrichment_status_is", label: "Enrichment status is" },
];

export const ACTION_TYPES: Array<{ value: ActionType; label: string; description: string }> = [
  { value: "send_webhook", label: "Send Webhook", description: "POST JSON to a URL" },
  { value: "tag_entity", label: "Tag Entity", description: "Append a concept tag" },
  { value: "send_alert", label: "Send Alert", description: "Fire a notification channel" },
  { value: "log_only", label: "Log Only", description: "Record run (no external calls)" },
];

export const emptyCondition = (): Condition => ({ type: "field_equals", field: "", value: "" });
export const emptyAction = (): Action => ({ type: "log_only", config: {} });
