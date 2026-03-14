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
  notes:            string | null;
  pinned:           boolean;
  context_snapshot: string;
  created_at:       string;
}

interface SessionDetail {
  id:               number;
  domain_id:        string;
  label:            string;
  notes:            string | null;
  pinned:           boolean;
  context_snapshot: Snapshot;
  created_at:       string;
}

interface DeltaValue { before: number; after: number; change: number }

interface DiffResult {
  snapshot_a_domain:    string;
  snapshot_b_domain:    string;
  snapshot_a_generated: string;
  snapshot_b_generated: string;
  entity_stats: Record<string, DeltaValue>;
  gaps:         Record<string, DeltaValue>;
  top_topics:   { concept: string; before: number; after: number; change: number }[];
}

interface Tool {
  name:        string;
  description: string;
  parameters:  Record<string, { type: string; default?: unknown }>;
}

// ── Helpers ────────────────────────────────────────────────────────────────────

function SnapshotCards({ snap }: { snap: Snapshot }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-blue-200 bg-blue-50 p-5 dark:border-blue-800 dark:bg-blue-900/10">
          <p className="text-xs font-medium text-blue-600 dark:text-blue-400">Total Entities</p>
          <p className="mt-1 text-3xl font-bold text-blue-700 dark:text-blue-300">{snap.entity_stats.total.toLocaleString()}</p>
          <p className="mt-1 text-xs text-blue-600 dark:text-blue-400">{snap.entity_stats.pct_enriched}% enriched</p>
        </div>
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 dark:border-red-800 dark:bg-red-900/10">
          <p className="text-xs font-medium text-red-600 dark:text-red-400">Data Gaps</p>
          <p className="mt-1 text-3xl font-bold text-red-700 dark:text-red-300">{snap.gaps.critical}</p>
          <p className="mt-1 text-xs text-red-600 dark:text-red-400">critical · {snap.gaps.warning} warnings</p>
        </div>
        <div className="rounded-xl border border-violet-200 bg-violet-50 p-5 dark:border-violet-800 dark:bg-violet-900/10">
          <p className="text-xs font-medium text-violet-600 dark:text-violet-400">Schema</p>
          <p className="mt-1 text-base font-bold text-violet-700 dark:text-violet-300 truncate">{snap.schema?.name || snap.domain_id}</p>
          <p className="mt-1 text-xs text-violet-600 dark:text-violet-400">{snap.schema?.attributes?.length ?? 0} attributes</p>
        </div>
      </div>
      {snap.top_topics.length > 0 && (
        <div className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-900">
          <h3 className="mb-3 text-sm font-semibold text-gray-900 dark:text-white">Top Concepts</h3>
          <div className="flex flex-wrap gap-2">
            {snap.top_topics.map((t) => (
              <span key={t.concept} className="inline-flex items-center gap-1 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-xs dark:border-gray-700 dark:bg-gray-800">
                <span className="font-medium text-gray-700 dark:text-gray-300">{t.concept}</span>
                <span className="text-gray-400 dark:text-gray-500">{t.count}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function DeltaTable({ title, rows }: { title: string; rows: { label: string; before: number; after: number; change: number }[] }) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900">
      <p className="border-b border-gray-200 px-5 py-3 text-sm font-semibold text-gray-900 dark:border-gray-700 dark:text-white">{title}</p>
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-5 py-2 text-left text-xs font-medium text-gray-500">Metric</th>
            <th className="px-5 py-2 text-right text-xs font-medium text-gray-500">Before</th>
            <th className="px-5 py-2 text-right text-xs font-medium text-gray-500">After</th>
            <th className="px-5 py-2 text-right text-xs font-medium text-gray-500">Change</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.label} className="border-t border-gray-100 dark:border-gray-800">
              <td className="px-5 py-2 font-medium capitalize text-gray-800 dark:text-gray-200">{r.label.replace(/_/g, " ")}</td>
              <td className="px-5 py-2 text-right text-gray-500">{r.before}</td>
              <td className="px-5 py-2 text-right text-gray-700 dark:text-gray-300">{r.after}</td>
              <td className={`px-5 py-2 text-right font-semibold ${r.change > 0 ? "text-green-600" : r.change < 0 ? "text-red-500" : "text-gray-400"}`}>
                {r.change > 0 ? "+" : ""}{r.change}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function ContextPage() {
  const { activeDomainId } = useDomain();

  const [tab, setTab] = useState<"snapshot" | "sessions" | "diff" | "tools">("snapshot");

  // Snapshot
  const [snapshot, setSnapshot]   = useState<Snapshot | null>(null);
  const [loadingSnap, setLoadingSnap] = useState(false);
  const [saveLabel, setSaveLabel]  = useState("");
  const [saving, setSaving]        = useState(false);
  const [snapError, setSnapError]  = useState<string | null>(null);

  // Sessions
  const [sessions, setSessions]           = useState<Session[]>([]);
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [editingNotes, setEditingNotes]   = useState<Record<number, string>>({});
  const [savingNotes, setSavingNotes]     = useState<Record<number, boolean>>({});

  // Diff
  const [diffA, setDiffA]           = useState<number | "">("");
  const [diffB, setDiffB]           = useState<number | "">("");
  const [diffResult, setDiffResult] = useState<DiffResult | null>(null);
  const [diffLoading, setDiffLoading] = useState(false);
  const [diffError, setDiffError]   = useState<string | null>(null);

  // Tools
  const [tools, setTools]               = useState<Tool[]>([]);
  const [loadingTools, setLoadingTools] = useState(false);
  const [selectedTool, setSelectedTool] = useState<string>("");
  const [toolParams, setToolParams]     = useState<Record<string, string>>({});
  const [toolResult, setToolResult]     = useState<unknown>(null);
  const [invoking, setInvoking]         = useState(false);
  const [toolError, setToolError]       = useState<string | null>(null);

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

  useEffect(() => {
    if (tab === "sessions" || tab === "diff") fetchSessions();
  }, [tab, fetchSessions]);

  const fetchSessionDetail = async (id: number) => {
    setLoadingDetail(true);
    setSelectedSession(null);
    try {
      const res = await apiFetch(`/context/sessions/${id}`);
      if (res.ok) setSelectedSession(await res.json());
    } finally { setLoadingDetail(false); }
  };

  const deleteSession = async (id: number) => {
    await apiFetch(`/context/sessions/${id}`, { method: "DELETE" });
    setSessions((prev) => prev.filter((s) => s.id !== id));
    if (selectedSession?.id === id) setSelectedSession(null);
  };

  const patchSession = async (id: number, patch: { label?: string; notes?: string; pinned?: boolean }) => {
    setSavingNotes((p) => ({ ...p, [id]: true }));
    try {
      await apiFetch(`/context/sessions/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(patch),
      });
      setSessions((prev) => prev.map((s) => s.id === id ? { ...s, ...patch } : s));
      if (selectedSession?.id === id) {
        setSelectedSession((prev) => prev ? { ...prev, ...patch } : prev);
      }
    } finally { setSavingNotes((p) => ({ ...p, [id]: false })); }
  };

  const sortedSessions = [...sessions].sort(
    (a, b) => Number(b.pinned) - Number(a.pinned) || new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  // ── Diff ────────────────────────────────────────────────────────────────────

  const runDiff = async () => {
    if (!diffA || !diffB) return;
    setDiffLoading(true);
    setDiffError(null);
    setDiffResult(null);
    try {
      const res = await apiFetch(`/context/sessions/diff?a=${diffA}&b=${diffB}`);
      if (!res.ok) { setDiffError(await res.text()); return; }
      setDiffResult(await res.json());
    } catch { setDiffError("Network error"); }
    finally { setDiffLoading(false); }
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

  const TAB_LABELS: Record<string, string> = {
    snapshot: "Live Snapshot",
    sessions: "Saved Sessions",
    diff:     "Session Diff",
    tools:    "Tool Explorer",
  };

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Context Engineering" },
        ]}
        title="Context Engineering"
        description="Domain context snapshots, memory sessions, diff analysis, and tool invocations"
      />

      {/* Tabs */}
      <div className="flex gap-1 rounded-xl border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
        {(["snapshot", "sessions", "diff", "tools"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              tab === t
                ? "bg-white text-gray-900 shadow-sm dark:bg-gray-900 dark:text-white"
                : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            }`}
          >
            {TAB_LABELS[t]}
          </button>
        ))}
      </div>

      {/* ── Live Snapshot ──────────────────────────────────────────────────────── */}
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
              <SnapshotCards snap={snapshot} />
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
                  {saving ? "Saving…" : "Save to Memory"}
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

      {/* ── Saved Sessions ─────────────────────────────────────────────────────── */}
      {tab === "sessions" && (
        <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
          {/* Session list */}
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
            {sortedSessions.map((s) => (
              <div key={s.id} className={`rounded-xl border bg-white px-5 py-4 shadow-sm dark:bg-gray-900 ${selectedSession?.id === s.id ? "border-blue-400 dark:border-blue-600" : "border-gray-200 dark:border-gray-700"}`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      {/* Pin toggle */}
                      <button
                        onClick={() => patchSession(s.id, { pinned: !s.pinned })}
                        title={s.pinned ? "Unpin" : "Pin"}
                        className={`text-lg leading-none ${s.pinned ? "text-amber-400" : "text-gray-300 hover:text-amber-300"}`}
                      >
                        {s.pinned ? "★" : "☆"}
                      </button>
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{s.label || `Snapshot #${s.id}`}</p>
                    </div>
                    <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500">
                      Domain: <span className="font-medium">{s.domain_id}</span> · {new Date(s.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <button
                      onClick={() => fetchSessionDetail(s.id)}
                      className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100 dark:border-blue-800 dark:bg-blue-900/10 dark:text-blue-400"
                    >
                      Details
                    </button>
                    <button
                      onClick={() => deleteSession(s.id)}
                      className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 dark:border-red-800 dark:bg-red-900/10 dark:text-red-400"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {/* Inline notes editor */}
                <div className="mt-3 flex gap-2">
                  <textarea
                    rows={2}
                    value={editingNotes[s.id] ?? s.notes ?? ""}
                    onChange={(e) => setEditingNotes((p) => ({ ...p, [s.id]: e.target.value }))}
                    placeholder="Add notes…"
                    className="flex-1 resize-none rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-700 focus:border-blue-400 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                  />
                  <button
                    disabled={savingNotes[s.id]}
                    onClick={() => patchSession(s.id, { notes: editingNotes[s.id] ?? s.notes ?? "" })}
                    className="self-end rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-200 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300"
                  >
                    {savingNotes[s.id] ? "…" : "Save"}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Detail panel */}
          <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
            {loadingDetail && <div className="h-48 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-700" />}
            {!loadingDetail && !selectedSession && (
              <p className="text-center text-sm text-gray-400 dark:text-gray-500 py-12">Select a session to view details</p>
            )}
            {selectedSession && (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    {selectedSession.label || `Snapshot #${selectedSession.id}`}
                  </p>
                  <span className="rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                    {selectedSession.domain_id}
                  </span>
                </div>
                <p className="text-xs text-gray-400">{new Date(selectedSession.created_at).toLocaleString()}</p>
                {selectedSession.notes && (
                  <p className="text-xs italic text-gray-500 dark:text-gray-400">{selectedSession.notes}</p>
                )}
                <SnapshotCards snap={selectedSession.context_snapshot} />
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── Session Diff ───────────────────────────────────────────────────────── */}
      {tab === "diff" && (
        <div className="space-y-6">
          {/* Selectors */}
          <div className="flex flex-col gap-4 rounded-2xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-900 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">Snapshot A (older)</label>
              <select
                value={diffA}
                onChange={(e) => setDiffA(Number(e.target.value) || "")}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
              >
                <option value="">Select session…</option>
                {sortedSessions.map((s) => (
                  <option key={s.id} value={s.id}>{s.label || `Snapshot #${s.id}`} — {s.domain_id}</option>
                ))}
              </select>
            </div>
            <div className="hidden items-center text-gray-400 sm:flex">→</div>
            <div className="flex-1">
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">Snapshot B (newer)</label>
              <select
                value={diffB}
                onChange={(e) => setDiffB(Number(e.target.value) || "")}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
              >
                <option value="">Select session…</option>
                {sortedSessions.map((s) => (
                  <option key={s.id} value={s.id}>{s.label || `Snapshot #${s.id}`} — {s.domain_id}</option>
                ))}
              </select>
            </div>
            <button
              onClick={runDiff}
              disabled={!diffA || !diffB || diffLoading}
              className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-6 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
            >
              {diffLoading ? "Comparing…" : "Compare"}
            </button>
          </div>

          {diffError && (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">{diffError}</div>
          )}

          {diffResult && (
            <div className="space-y-4">
              {/* Header */}
              <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400">
                <span>A: <strong>{diffResult.snapshot_a_domain}</strong> · {new Date(diffResult.snapshot_a_generated).toLocaleString()}</span>
                <span className="mx-2">→</span>
                <span>B: <strong>{diffResult.snapshot_b_domain}</strong> · {new Date(diffResult.snapshot_b_generated).toLocaleString()}</span>
              </div>

              <DeltaTable
                title="Entity Stats"
                rows={Object.entries(diffResult.entity_stats).map(([k, v]) => ({ label: k, ...v }))}
              />
              <DeltaTable
                title="Data Gaps"
                rows={Object.entries(diffResult.gaps).map(([k, v]) => ({ label: k, ...v }))}
              />
              {diffResult.top_topics.filter((t) => t.change !== 0).length > 0 && (
                <DeltaTable
                  title="Concept Changes"
                  rows={diffResult.top_topics
                    .filter((t) => t.change !== 0)
                    .sort((a, b) => Math.abs(b.change) - Math.abs(a.change))
                    .map((t) => ({ label: t.concept, before: t.before, after: t.after, change: t.change }))}
                />
              )}
            </div>
          )}

          {!diffResult && !diffLoading && !diffError && (
            <div className="flex flex-col items-center py-16 text-center">
              <span className="text-4xl">⚖️</span>
              <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">Select two sessions and click Compare to see the delta.</p>
            </div>
          )}
        </div>
      )}

      {/* ── Tool Explorer ─────────────────────────────────────────────────────── */}
      {tab === "tools" && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
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

          {selectedTool && (() => {
            const tool = tools.find((t) => t.name === selectedTool);
            if (!tool) return null;
            return (
              <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-900">
                <h3 className="font-mono text-sm font-semibold text-gray-900 dark:text-white">{tool.name}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">{tool.description}</p>
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
