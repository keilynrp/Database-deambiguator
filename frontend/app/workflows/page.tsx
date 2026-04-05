"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "../../lib/api";
import { ManualRunDialog, RunHistoryPanel } from "./WorkflowDialogs";
import { WorkflowForm } from "./WorkflowForm";
import { WorkflowList } from "./WorkflowList";
import type { Workflow } from "./workflowTypes";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [editing, setEditing] = useState<Workflow | null>(null);
  const [historyFor, setHistoryFor] = useState<number | null>(null);
  const [manualRunFor, setManualRunFor] = useState<number | null>(null);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const response = await apiFetch("/workflows");
      const data = await response.json();
      setWorkflows(data.items || []);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;

    setLoading(true);
    apiFetch("/workflows")
      .then((response) => response.json())
      .then((data) => {
        if (!cancelled) {
          setWorkflows(data.items || []);
        }
      })
      .catch((e: unknown) => {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Load failed");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleCreate = async (data: Partial<Workflow>) => {
    try {
      await apiFetch("/workflows", { method: "POST", body: JSON.stringify(data) });
      setShowCreate(false);
      load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Create failed");
    }
  };

  const handleUpdate = async (data: Partial<Workflow>) => {
    if (!editing) {
      return;
    }
    try {
      await apiFetch(`/workflows/${editing.id}`, { method: "PUT", body: JSON.stringify(data) });
      setEditing(null);
      load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Update failed");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this workflow?")) {
      return;
    }
    try {
      await apiFetch(`/workflows/${id}`, { method: "DELETE" });
      load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Delete failed");
    }
  };

  const handleToggle = async (workflow: Workflow) => {
    try {
      await apiFetch(`/workflows/${workflow.id}`, {
        method: "PUT",
        body: JSON.stringify({ is_active: !workflow.is_active }),
      });
      load();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Toggle failed");
    }
  };

  const openCreate = () => {
    setShowCreate(true);
    setEditing(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-violet-50 p-6">
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Workflow Automation</h1>
            <p className="mt-1 text-sm text-slate-500">
              Build no-code trigger - condition - action chains to automate data operations.
            </p>
          </div>
          <button
            type="button"
            onClick={openCreate}
            className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-violet-700"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Workflow
          </button>
        </div>

        {error && (
          <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}

        {(showCreate || editing) && (
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-5 text-lg font-semibold text-slate-900">
              {editing ? "Edit Workflow" : "New Workflow"}
            </h2>
            <WorkflowForm
              initial={editing ?? undefined}
              onSave={editing ? handleUpdate : handleCreate}
              onCancel={() => {
                setShowCreate(false);
                setEditing(null);
              }}
            />
          </div>
        )}

        <WorkflowList
          loading={loading}
          showCreate={showCreate}
          workflows={workflows}
          onCreate={openCreate}
          onToggle={handleToggle}
          onRun={setManualRunFor}
          onHistory={setHistoryFor}
          onEdit={(workflow) => {
            setEditing(workflow);
            setShowCreate(false);
          }}
          onDelete={handleDelete}
        />
      </div>

      {historyFor !== null && (
        <RunHistoryPanel workflowId={historyFor} onClose={() => setHistoryFor(null)} />
      )}
      {manualRunFor !== null && (
        <ManualRunDialog
          workflowId={manualRunFor}
          onClose={() => setManualRunFor(null)}
          onComplete={() => {
            setManualRunFor(null);
            load();
          }}
        />
      )}
    </div>
  );
}
