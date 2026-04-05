"use client";

import { useEffect, useState } from "react";

import { apiFetch } from "../../lib/api";
import { STATUS_COLORS, type WorkflowRun } from "./workflowTypes";

export function RunHistoryPanel({ workflowId, onClose }: { workflowId: number; onClose: () => void }) {
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiFetch(`/workflows/${workflowId}/runs`)
      .then((response) => response.json())
      .then((data) => setRuns(data.items || []))
      .finally(() => setLoading(false));
  }, [workflowId]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="flex max-h-[80vh] w-full max-w-2xl flex-col rounded-xl bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-slate-900">Execution History</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <p className="text-sm text-slate-400">Loading runs...</p>
          ) : runs.length === 0 ? (
            <p className="text-sm text-slate-400">No runs yet.</p>
          ) : (
            <div className="space-y-3">
              {runs.map((run) => (
                <div key={run.id} className="rounded-lg border border-slate-200 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${STATUS_COLORS[run.status] || "bg-slate-100 text-slate-700"}`}
                      >
                        {run.status}
                      </span>
                      <span className="text-xs text-slate-500">
                        {run.started_at ? new Date(run.started_at).toLocaleString() : "-"}
                      </span>
                    </div>
                    {run.completed_at && run.started_at && (
                      <span className="text-xs text-slate-400">
                        {Math.round(
                          new Date(run.completed_at).getTime() - new Date(run.started_at).getTime(),
                        )}
                        ms
                      </span>
                    )}
                  </div>
                  {run.steps_log.length > 0 && (
                    <div className="space-y-1">
                      {run.steps_log.map((step, index) => (
                        <div key={index} className="flex items-center gap-2 text-xs text-slate-600">
                          <span className={step.result.ok ? "text-emerald-500" : "text-rose-500"}>
                            {step.result.ok ? "OK" : "ERR"}
                          </span>
                          <span className="font-mono">{step.action}</span>
                          {!step.result.ok && (
                            <span className="text-rose-500">{String(step.result.error || "")}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  {run.error && <p className="mt-1 text-xs text-rose-600">{run.error}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export function ManualRunDialog({
  workflowId,
  onClose,
  onComplete,
}: {
  workflowId: number;
  onClose: () => void;
  onComplete: () => void;
}) {
  const [entityId, setEntityId] = useState("");
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<WorkflowRun | null>(null);
  const [error, setError] = useState("");

  const handleRun = async () => {
    if (!entityId) {
      return;
    }
    setRunning(true);
    setError("");
    try {
      const response = await apiFetch(`/workflows/${workflowId}/run`, {
        method: "POST",
        body: JSON.stringify({ entity_id: parseInt(entityId, 10) }),
      });
      const run = await response.json();
      setResult(run);
      onComplete();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Run failed");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-2xl">
        <h2 className="mb-4 text-lg font-semibold text-slate-900">Manual Run</h2>
        {!result ? (
          <>
            <label className="mb-1 block text-sm font-medium text-slate-700">Entity ID</label>
            <input
              type="number"
              value={entityId}
              onChange={(e) => setEntityId(e.target.value)}
              placeholder="Enter entity ID"
              className="mb-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            />
            {error && <p className="mb-3 text-sm text-rose-600">{error}</p>}
            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="text-sm text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleRun}
                disabled={!entityId || running}
                className="rounded-lg bg-violet-600 px-5 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
              >
                {running ? "Running..." : "Run Now"}
              </button>
            </div>
          </>
        ) : (
          <>
            <div
              className={`mb-3 inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${STATUS_COLORS[result.status] || "bg-slate-100"}`}
            >
              {result.status}
            </div>
            <div className="mb-4 space-y-1">
              {result.steps_log.map((step, index) => (
                <div key={index} className="flex items-center gap-2 text-sm">
                  <span className={step.result.ok ? "text-emerald-500" : "text-rose-500"}>
                    {step.result.ok ? "OK" : "ERR"}
                  </span>
                  <span className="font-mono text-xs">{step.action}</span>
                </div>
              ))}
            </div>
            <button
              type="button"
              onClick={onClose}
              className="w-full rounded-lg bg-slate-100 py-2 text-sm text-slate-700 hover:bg-slate-200"
            >
              Close
            </button>
          </>
        )}
      </div>
    </div>
  );
}
