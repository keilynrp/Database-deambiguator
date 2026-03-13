"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { useDomain } from "../contexts/DomainContext";
import { PageHeader } from "../components/ui";

// ── Types ──────────────────────────────────────────────────────────────────────

interface EntityStats { total: number; enriched: number; pct_enriched: number }
interface GapSummary  { critical: number; warning: number; ok: number }
interface TopTopic    { concept: string; count: number }

interface Snapshot {
  domain_id:    string;
  generated_at: string;
  schema:       { name?: string; primary_entity?: string; attributes?: unknown[] };
  entity_stats: EntityStats;
  gaps:         GapSummary;
  top_topics:   TopTopic[];
}

interface Session {
  id:               number;
  domain_id:        string;
  label:            string;
  context_snapshot: string;
  created_at:       string;
}

interface Tool {
  name:        string;
  description: string;
  parameters:  Record<string, { type: string; default?: unknown }>;
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function ContextPage() {
  const { activeDomainId } = useDomain();

  // Tabs
  const [tab, setTab] = useState<"snapshot" | "sessions" | "tools">("snapshot");

  // Snapshot
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [loadingSnap, setLoadingSnap] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);
  const [snapError, setSnapError] = useState<string | null>(null);

  // Sessions
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);

  // Tools
  const [tools, setTools] = useState<Tool[]>([]);
  const [loadingTools, setLoadingTools] = useState(false);
  const [selectedTool, setSelectedTool] = useState<string>("");
  const [toolParams, setToolParams] = useState<Record<string, string>>({});
  const [toolResult, setToolResult] = useState<unknown>(null);
  const [invoking, setInvoking] = useState(false);
  const [toolError, setToolError] = useState<string | null>(null);

  // ── Snapshot ────────────────────────────────────────────────────────────────

  const fetchSnapshot = useCallback(async () => {
    if (!activeDomainId) return;
    setLoadingSnap(true);
    setSnapError(null);
    try {
      const res = await apiFetch(`/context/snapshot/${activeDomainId}`);
      if (!res.ok) { setSnapError(await res.text()); return; }
      setSnapshot(await res.json());
    } catch { setSnapError("Network error"); }
    finally { setLoadingSnap(false); }
  }, [activeDomainId]);

  useEffect(() => { if (tab === "snapshot") fetchSnapshot(); }, [tab, fetchSnapshot]);

  const saveSnapshot = async () => {
    if (!activeDomainId) return;
    setSaving(true);
    try {
      await apiFetch("/context/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain_id: activeDomainId, label: saveLabel || "" }),
      });
      setSaveLabel("");
      if (tab === "sessions") fetchSessions();
    } finally { setSaving(false); }
  };

  // ── Sessions ────────────────────────────────────────────────────────────────

  const fetchSessions = useCallback(async () => {
    setLoadingSessions(true);
    try {
      const res = await apiFetch("/context/sessions");
      if (res.ok) setSessions(await res.json());
    } finally { setLoadingSessions(false); }
  }, []);

  useEffect(() => { if (tab === "sessions") fetchSessions(); }, [tab, fetchSessions]);

  const deleteSession = async (id: number) => {
    await apiFetch(`/context/sessions/${id}`, { method: "DELETE" });
    setSessions((prev) => prev.filter((s) => s.id !== id));
  };

  // ── Tools ───────────────────────────────────────────────────────────────────

  const fetchTools = useCallback(async () => {
    if (tools.length) return;
    setLoadingTools(true);
    try {
      const res = await apiFetch("/context/tools");
      if (res.ok) {
        const data: Tool[] = await res.json();
        setTools(data);
        if (data.length) {
          setSelectedTool(data[0].name);
          const defaults: Record<string, string> = {};
          Object.entries(data[0].parameters).forEach(([k, v]) => {
            defaults[k] = String(v.default ?? "");
          });
          setToolParams({ ...defaults, domain_id: activeDomainId || "default" });
        }
      }
    } finally { setLoadingTools(false); }
  }, [tools.length, activeDomainId]);

  useEffect(() => { if (tab === "tools") fetchTools(); }, [tab, fetchTools]);

  const onSelectTool = (name: string) => {
    setSelectedTool(name);
    setToolResult(null);
    setToolError(null);
    const tool = tools.find((t) => t.name === name);
    if (tool) {
      const defaults: Record<string, string> = {};
      Object.entries(tool.parameters).forEach(([k, v]) => {
        defaults[k] = String(v.default ?? "");
      });
      setToolParams({ ...defaults, domain_id: activeDomainId || "default" });
    }
  };

  const invokeTool = async () => {
    setInvoking(true);
    setToolResult(null);
    setToolError(null);
    try {
      const params: Record<string, unknown> = {};
      Object.entries(toolParams).forEach(([k, v]) => {
        params[k] = isNaN(Number(v)) ? v : Number(v);
      });
      const res = await apiFetch("/context/invoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tool: selectedTool, params }),
      });
      const data = await res.json();
      if (!res.ok) { setToolError(data.detail ?? JSON.stringify(data)); return; }
      setToolResult(data.result);
    } catch { setToolError("Network error"); }
    finally { setInvoking(false); }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Context Engineering" },
        ]}
        title="Context Engineering"
        description="Domain context snapshots, analysis sessions, and tool invocations"
      />

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
        {(["snapshot", "sessions", "tools"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium capitalize transition-all ${
              tab === t
                ? "bg-white text-gray-900 shadow-sm dark:bg-gray-900 dark:text-white"
                : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            }`}
          >
            {t === "snapshot" ? "Live Snapshot" : t === "sessions" ? "Saved Sessions" : "Tool Explorer"}
          </button>
        ))}
      </div>

      {/* ── Live Snapshot Tab ─────────────────────────────────────────────────── */}
      {tab === "snapshot" && (
        <div className="space-y-4">
          {snapError && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">{snapError}</div>
          )}
          {loadingSnap && !snapshot && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {[1, 2, 3].map((i) => <div key={i} className="h-24 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />)}
            </div>
          )}
          {snapshot && (
            <>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {/* Entity stats */}
                <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 dark:border-blue-800 dark:bg-blue-900/10">
                  <p className="text-xs font-medium text-blue-600 dark:text-blue-400">Total Entities</p>
                  <p className="mt-1 text-3xl font-bold text-blue-700 dark:text-blue-300">{snapshot.entity_stats.total.toLocaleString()}</p>
                  <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">{snapshot.entity_stats.pct_enriched}% enriched</p>
                </div>
                {/* Gaps */}
                <div className="rounded-xl border border-red-200 bg-red-50 p-5 dark:border-red-800 dark:bg-red-900/10">
                  <p className="text-xs font-medium text-red-600 dark:text-red-400">Data Gaps</p>
                  <p className="mt-1 text-3xl font-bold text-red-700 dark:text-red-300">{snapshot.gaps.critical}</p>
                  <p className="mt-1 text-xs text-red-600 dark:text-red-400">critical · {snapshot.gaps.warning} warnings</p>
                </div>
                {/* Schema */}
                <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 dark:border-violet-800 dark:bg-violet-900/10">
                  <p className="text-xs font-medium text-violet-600 dark:text-violet-400">Schema</p>
                  <p className="mt-1 text-base font-bold text-violet-700 dark:text-violet-300 truncate">{snapshot.schema.name || snapshot.domain_id}</p>
                  <p className="mt-1 text-xs text-violet-600 dark:text-violet-400">{snapshot.schema.attributes?.length ?? 0} attributes</p>
                </div>
              </div>

              {/* Top Topics */}
              {snapshot.top_topics.length > 0 && (
                <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-900">
                  <h3 className="mb-3 text-sm font-semibold text-gray-900 dark:text-white">Top Concepts</h3>
                  <div className="flex flex-wrap gap-2">
                    {snapshot.top_topics.map((t) => (
                      <span key={t.concept} className="inline-flex items-center gap-1 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs dark:border-gray-700 dark:bg-gray-800">
                        <span className="font-medium text-gray-700 dark:text-gray-300">{t.concept}</span>
                        <span className="text-gray-400 dark:text-gray-500">{t.count}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Save as session */}
              <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
                <input
                  type="text"
                  value={saveLabel}
                  onChange={(e) => setSaveLabel(e.target.value)}
                  placeholder="Session label (optional)…"
                  className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500"
                />
                <button
                  onClick={saveSnapshot}
                  disabled={saving}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {saving ? "Saving…" : "Save Snapshot"}
                </button>
                <button
                  onClick={fetchSnapshot}
                  disabled={loadingSnap}
                  className="inline-flex items-center gap-1 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:bg-gray-900 dark:text-gray-400"
                >
                  Refresh
                </button>
              </div>
              <p className="text-right text-xs text-gray-400 dark:text-gray-600">
                Generated {new Date(snapshot.generated_at).toLocaleString()}
              </p>
            </>
          )}
        </div>
      )}

      {/* ── Saved Sessions Tab ─────────────────────────────────────────────────── */}
      {tab === "sessions" && (
        <div className="space-y-3">
          {loadingSessions && (
            <div className="space-y-3">{[1, 2, 3].map((i) => <div key={i} className="h-16 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />)}</div>
          )}
          {!loadingSessions && sessions.length === 0 && (
            <div className="flex flex-col items-center py-16 text-center">
              <span className="text-4xl">💾</span>
              <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">No saved sessions yet. Capture a snapshot from the Live Snapshot tab.</p>
            </div>
          )}
          {sessions.map((s) => (
            <div key={s.id} className="flex items-center justify-between rounded-xl border border-gray-200 bg-white px-5 py-4 shadow-sm dark:border-gray-700 dark:bg-gray-900">
              <div className="min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{s.label || `Snapshot #${s.id}`}</p>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  Domain: {s.domain_id} · {new Date(s.created_at).toLocaleString()}
                </p>
              </div>
              <button
                onClick={() => deleteSession(s.id)}
                className="ml-4 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 dark:border-red-800 dark:bg-red-900/10 dark:text-red-400"
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── Tool Explorer Tab ─────────────────────────────────────────────────── */}
      {tab === "tools" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
          {/* Tool list */}
          <div className="space-y-2">
            {loadingTools && <div className="h-48 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />}
            {tools.map((t) => (
              <button
                key={t.name}
                onClick={() => onSelectTool(t.name)}
                className={`w-full rounded-xl border p-4 text-left transition-all ${
                  selectedTool === t.name
                    ? "border-blue-300 bg-blue-50 dark:border-blue-500/40 dark:bg-blue-500/10"
                    : "border-gray-200 bg-white hover:border-gray-300 dark:border-gray-700 dark:bg-gray-900"
                }`}
              >
                <p className="text-sm font-mono font-medium text-gray-900 dark:text-white">{t.name}</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400 line-clamp-2">{t.description}</p>
              </button>
            ))}
          </div>

          {/* Invocation panel */}
          {selectedTool && (() => {
            const tool = tools.find((t) => t.name === selectedTool);
            if (!tool) return null;
            return (
              <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
                <h3 className="font-mono text-sm font-semibold text-gray-900 dark:text-white">{tool.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{tool.description}</p>

                {/* Param inputs */}
                <div className="space-y-3">
                  {Object.entries(tool.parameters).map(([k, v]) => (
                    <div key={k}>
                      <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                        {k} <span className="text-gray-400">({v.type})</span>
                      </label>
                      <input
                        type="text"
                        value={toolParams[k] ?? String(v.default ?? "")}
                        onChange={(e) => setToolParams((p) => ({ ...p, [k]: e.target.value }))}
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 font-mono text-sm text-gray-900 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                      />
                    </div>
                  ))}
                </div>

                <button
                  onClick={invokeTool}
                  disabled={invoking}
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {invoking ? "Running…" : "Run Tool"}
                </button>

                {toolError && (
                  <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">{toolError}</div>
                )}
                {toolResult !== null && (
                  <div className="rounded-xl border border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-800">
                    <p className="border-b border-gray-200 px-4 py-2 text-xs font-medium text-gray-500 dark:border-gray-700 dark:text-gray-400">Result</p>
                    <pre className="max-h-64 overflow-auto p-4 text-xs text-gray-800 dark:text-gray-200">
                      {JSON.stringify(toolResult, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
