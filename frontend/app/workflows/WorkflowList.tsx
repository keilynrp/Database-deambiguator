"use client";

import {
  STATUS_COLORS,
  TRIGGER_COLORS,
  TRIGGER_LABELS,
  type Workflow,
} from "./workflowTypes";

function Badge({ label, className }: { label: string; className: string }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}

function WorkflowCard({
  workflow,
  onToggle,
  onRun,
  onHistory,
  onEdit,
  onDelete,
}: {
  workflow: Workflow;
  onToggle: (workflow: Workflow) => void;
  onRun: (workflowId: number) => void;
  onHistory: (workflowId: number) => void;
  onEdit: (workflow: Workflow) => void;
  onDelete: (workflowId: number) => void;
}) {
  return (
    <div
      className={`rounded-xl border bg-white p-5 shadow-sm transition-opacity dark:bg-slate-900 ${workflow.is_active ? "border-slate-200 dark:border-slate-700" : "border-slate-100 opacity-60 dark:border-slate-800"}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="truncate font-semibold text-slate-900 dark:text-white">{workflow.name}</h3>
            <Badge
              label={TRIGGER_LABELS[workflow.trigger_type] || workflow.trigger_type}
              className={TRIGGER_COLORS[workflow.trigger_type] || "bg-slate-100 text-slate-700"}
            />
            {!workflow.is_active && <Badge label="Inactive" className="bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400" />}
            {workflow.last_run_status && (
              <Badge
                label={workflow.last_run_status}
                className={STATUS_COLORS[workflow.last_run_status] || "bg-slate-100 text-slate-700"}
              />
            )}
          </div>
          {workflow.description && <p className="mt-1 truncate text-sm text-slate-500 dark:text-slate-400">{workflow.description}</p>}
          <div className="mt-2 flex items-center gap-4 text-xs text-slate-400 dark:text-slate-500">
            <span>
              {workflow.conditions.length} condition{workflow.conditions.length !== 1 ? "s" : ""}
            </span>
            <span>{workflow.actions.length} action{workflow.actions.length !== 1 ? "s" : ""}</span>
            <span>{workflow.run_count} run{workflow.run_count !== 1 ? "s" : ""}</span>
            {workflow.last_run_at && (
              <span>Last run {new Date(workflow.last_run_at).toLocaleDateString()}</span>
            )}
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => onToggle(workflow)}
            title={workflow.is_active ? "Deactivate" : "Activate"}
            className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${workflow.is_active ? "bg-violet-600" : "bg-slate-300 dark:bg-slate-700"}`}
          >
            <span
              className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white shadow transition-transform ${workflow.is_active ? "translate-x-4" : "translate-x-1"}`}
            />
          </button>

          <button
            type="button"
            onClick={() => onRun(workflow.id)}
            title="Manual run"
            className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:border-violet-300 hover:text-violet-600 dark:border-slate-700 dark:text-slate-400 dark:hover:border-violet-500 dark:hover:text-violet-300"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
            </svg>
          </button>

          <button
            type="button"
            onClick={() => onHistory(workflow.id)}
            title="Run history"
            className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:border-violet-300 hover:text-violet-600 dark:border-slate-700 dark:text-slate-400 dark:hover:border-violet-500 dark:hover:text-violet-300"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </button>

          <button
            type="button"
            onClick={() => onEdit(workflow)}
            title="Edit"
            className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:border-violet-300 hover:text-violet-600 dark:border-slate-700 dark:text-slate-400 dark:hover:border-violet-500 dark:hover:text-violet-300"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931z" />
            </svg>
          </button>

          <button
            type="button"
            onClick={() => onDelete(workflow.id)}
            title="Delete"
            className="rounded-lg border border-slate-200 p-1.5 text-slate-500 hover:border-rose-200 hover:text-rose-600 dark:border-slate-700 dark:text-slate-400 dark:hover:border-rose-500 dark:hover:text-rose-300"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

export function WorkflowList({
  loading,
  showCreate,
  workflows,
  onCreate,
  onToggle,
  onRun,
  onHistory,
  onEdit,
  onDelete,
}: {
  loading: boolean;
  showCreate: boolean;
  workflows: Workflow[];
  onCreate: () => void;
  onToggle: (workflow: Workflow) => void;
  onRun: (workflowId: number) => void;
  onHistory: (workflowId: number) => void;
  onEdit: (workflow: Workflow) => void;
  onDelete: (workflowId: number) => void;
}) {
  if (loading) {
    return <div className="py-16 text-center text-slate-400 dark:text-slate-500">Loading workflows...</div>;
  }

  if (workflows.length === 0 && !showCreate) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-16 text-center dark:border-slate-800 dark:bg-slate-900">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-violet-100 dark:bg-violet-500/20">
          <svg className="h-8 w-8 text-violet-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-slate-800 dark:text-white">No workflows yet</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Create your first workflow to automate data operations.</p>
        <button
          type="button"
          onClick={onCreate}
          className="mt-4 rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700"
        >
          Create Workflow
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {workflows.map((workflow) => (
        <WorkflowCard
          key={workflow.id}
          workflow={workflow}
          onToggle={onToggle}
          onRun={onRun}
          onHistory={onHistory}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
