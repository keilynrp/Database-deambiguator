"use client";

import { useState, useEffect, useCallback } from "react";
import { PageHeader } from "../components/ui";
import { apiFetch } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface ScraperConfig {
  id: number;
  name: string;
  url_template: string;
  selector_type: string;
  selector: string;
  field_map: Record<string, string>;
  rate_limit_secs: number;
  is_active: boolean;
  last_run_at: string | null;
  last_run_status: string | null;
  total_runs: number;
  total_enriched: number;
  created_at: string;
}

const BLANK: Omit<ScraperConfig, "id" | "last_run_at" | "last_run_status" | "total_runs" | "total_enriched" | "created_at"> = {
  name: "",
  url_template: "",
  selector_type: "css",
  selector: "",
  field_map: {},
  rate_limit_secs: 1.0,
  is_active: true,
};

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusBadge(status: string | null) {
  if (!status) return null;
  const cls = status === "ok"
    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
    : "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300";
  return <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold ${cls}`}>{status}</span>;
}

// ── Field Map Editor ──────────────────────────────────────────────────────────

function FieldMapEditor({
  value,
  onChange,
}: {
  value: Record<string, string>;
  onChange: (v: Record<string, string>) => void;
}) {
  const entries = Object.entries(value);

  function add() {
    const idx = String(entries.length);
    onChange({ ...value, [idx]: "" });
  }

  function remove(key: string) {
    const next = { ...value };
    delete next[key];
    onChange(next);
  }

  function setField(key: string, field: string) {
    onChange({ ...value, [key]: field });
  }

  return (
    <div className="space-y-2">
      <p className="text-xs text-gray-500 dark:text-gray-400">
        Map each matched element (by index) to an entity field.
      </p>
      {entries.map(([key, field]) => (
        <div key={key} className="flex items-center gap-2">
          <span className="w-6 text-center text-xs font-mono text-gray-500">#{key}</span>
          <input
            type="text"
            value={field}
            placeholder="entity field (e.g. enrichment_concepts)"
            onChange={(e) => setField(key, e.target.value)}
            className="flex-1 h-8 rounded border border-gray-200 bg-white px-2 text-xs dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          />
          <button
            onClick={() => remove(key)}
            className="text-red-400 hover:text-red-600 text-xs"
          >
            ✕
          </button>
        </div>
      ))}
      <button
        onClick={add}
        className="text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
      >
        + Add mapping
      </button>
    </div>
  );
}

// ── Scraper Form ──────────────────────────────────────────────────────────────

function ScraperForm({
  initial,
  onSave,
  onCancel,
}: {
  initial: typeof BLANK & { id?: number };
  onSave: (data: typeof BLANK) => Promise<void>;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({ ...initial });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function set(key: string, val: unknown) {
    setForm((f) => ({ ...f, [key]: val }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSave(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div>
          <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Name *</label>
          <input
            required
            value={form.name}
            onChange={(e) => set("name", e.target.value)}
            className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            placeholder="My Wikipedia Scraper"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Selector Type</label>
          <select
            value={form.selector_type}
            onChange={(e) => set("selector_type", e.target.value)}
            className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          >
            <option value="css">CSS</option>
            <option value="xpath">XPath</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
          URL Template * <span className="font-normal">(use <code className="rounded bg-gray-100 px-1 dark:bg-gray-700">{"{"+"primary_label"+"}"}</code> as placeholder)</span>
        </label>
        <input
          required
          value={form.url_template}
          onChange={(e) => set("url_template", e.target.value)}
          className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white font-mono"
          placeholder="https://en.wikipedia.org/wiki/{primary_label}"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Selector *</label>
        <input
          required
          value={form.selector}
          onChange={(e) => set("selector", e.target.value)}
          className="w-full h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white font-mono"
          placeholder={form.selector_type === "css" ? "p.mw-parser-output" : "//div[@class='mw-parser-output']/p"}
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
          Rate limit (sec)
        </label>
        <input
          type="number"
          min={0.1}
          max={60}
          step={0.1}
          value={form.rate_limit_secs}
          onChange={(e) => set("rate_limit_secs", parseFloat(e.target.value))}
          className="w-32 h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">Field Mapping</label>
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-800/50">
          <FieldMapEditor value={form.field_map} onChange={(v) => set("field_map", v)} />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_active"
          checked={form.is_active}
          onChange={(e) => set("is_active", e.target.checked)}
          className="h-4 w-4 rounded border-gray-300"
        />
        <label htmlFor="is_active" className="text-sm text-gray-700 dark:text-gray-300">Active</label>
      </div>

      {error && <p className="text-sm text-red-600 dark:text-red-400">{error}</p>}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={saving}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving…" : "Save"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}

// ── Test Panel ────────────────────────────────────────────────────────────────

function TestPanel({ scraper }: { scraper: ScraperConfig }) {
  const [label, setLabel] = useState("");
  const [result, setResult] = useState<{ ok: boolean; fields?: Record<string, string>; error?: string } | null>(null);
  const [loading, setLoading] = useState(false);

  async function runTest() {
    if (!label.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await apiFetch(`/scrapers/${scraper.id}/test`, {
        method: "POST",
        body: JSON.stringify({ primary_label: label }),
      });
      setResult(await res.json());
    } catch {
      setResult({ ok: false, error: "Request failed" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="e.g. Python (programming language)"
          className="flex-1 h-9 rounded-lg border border-gray-200 bg-white px-3 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-white"
          onKeyDown={(e) => e.key === "Enter" && runTest()}
        />
        <button
          onClick={runTest}
          disabled={loading || !label.trim()}
          className="rounded-lg bg-violet-600 px-4 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-50"
        >
          {loading ? "Testing…" : "Test"}
        </button>
      </div>
      {result && (
        <div className={`rounded-lg p-3 text-sm ${result.ok ? "bg-emerald-50 dark:bg-emerald-900/20" : "bg-red-50 dark:bg-red-900/20"}`}>
          {result.ok ? (
            Object.keys(result.fields ?? {}).length > 0 ? (
              <pre className="text-xs text-emerald-800 dark:text-emerald-300 whitespace-pre-wrap">
                {JSON.stringify(result.fields, null, 2)}
              </pre>
            ) : (
              <p className="text-emerald-700 dark:text-emerald-300">No fields extracted — check your selector</p>
            )
          ) : (
            <p className="text-red-700 dark:text-red-300">{result.error}</p>
          )}
        </div>
      )}
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function ScrapersPage() {
  const [scrapers, setScrapers] = useState<ScraperConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<ScraperConfig | null>(null);
  const [testTarget, setTestTarget] = useState<ScraperConfig | null>(null);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [runResult, setRunResult] = useState<Record<number, { enriched: number; errors: number }>>({});

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/scrapers");
      setScrapers(await res.json());
    } catch {
      setScrapers([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleCreate(data: typeof BLANK) {
    const res = await apiFetch("/scrapers", {
      method: "POST",
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    setShowForm(false);
    load();
  }

  async function handleUpdate(data: typeof BLANK) {
    if (!editing) return;
    const res = await apiFetch(`/scrapers/${editing.id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`Server error ${res.status}`);
    setEditing(null);
    load();
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this scraper config?")) return;
    await apiFetch(`/scrapers/${id}`, { method: "DELETE" });
    load();
  }

  async function handleRun(s: ScraperConfig) {
    setRunningId(s.id);
    try {
      const res = await apiFetch(`/scrapers/${s.id}/run?limit=50`, { method: "POST" });
      const data = await res.json();
      setRunResult((prev) => ({
        ...prev,
        [s.id]: { enriched: data.enriched, errors: data.errors },
      }));
      load();
    } finally {
      setRunningId(null);
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Web Scrapers" },
        ]}
        title="Web Scraper Configs"
        description="Define URL-based enrichment sources using CSS/XPath selectors"
        actions={
          <button
            onClick={() => { setShowForm(true); setEditing(null); }}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + New Scraper
          </button>
        }
      />

      {/* Create form */}
      {showForm && !editing && (
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">New Scraper</h3>
          <ScraperForm
            initial={BLANK}
            onSave={handleCreate}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <svg className="h-8 w-8 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        </div>
      ) : scrapers.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-gray-300 p-12 text-center dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">No scraper configs yet. Create one above.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {scrapers.map((s) => (
            <div
              key={s.id}
              className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900"
            >
              <div className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-gray-900 dark:text-white truncate">{s.name}</h3>
                      {!s.is_active && (
                        <span className="rounded-full bg-gray-100 px-2 py-0.5 text-[10px] text-gray-500 dark:bg-gray-800">
                          disabled
                        </span>
                      )}
                      {statusBadge(s.last_run_status)}
                    </div>
                    <p className="mt-1 text-xs font-mono text-gray-500 dark:text-gray-400 truncate">{s.url_template}</p>
                    <div className="mt-1.5 flex flex-wrap gap-3 text-xs text-gray-400">
                      <span><span className="font-medium">{s.selector_type.toUpperCase()}</span>: <code className="font-mono">{s.selector}</code></span>
                      <span>Rate: {s.rate_limit_secs}s</span>
                      <span>Runs: {s.total_runs}</span>
                      <span>Enriched: {s.total_enriched}</span>
                      {s.last_run_at && <span>Last: {new Date(s.last_run_at).toLocaleString()}</span>}
                    </div>
                    {runResult[s.id] && (
                      <p className="mt-1.5 text-xs text-emerald-600 dark:text-emerald-400">
                        Last run: {runResult[s.id].enriched} enriched, {runResult[s.id].errors} errors
                      </p>
                    )}
                  </div>
                  <div className="flex shrink-0 gap-2">
                    <button
                      onClick={() => setTestTarget(testTarget?.id === s.id ? null : s)}
                      className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                    >
                      Test
                    </button>
                    <button
                      onClick={() => handleRun(s)}
                      disabled={runningId === s.id || !s.is_active}
                      className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-700 disabled:opacity-50"
                    >
                      {runningId === s.id ? "Running…" : "Run"}
                    </button>
                    <button
                      onClick={() => { setEditing(s); setShowForm(false); }}
                      className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(s.id)}
                      className="rounded-lg border border-red-200 px-3 py-1.5 text-xs font-medium text-red-600 hover:bg-red-50 dark:border-red-800 dark:text-red-400 dark:hover:bg-red-900/20"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {/* Test panel */}
                {testTarget?.id === s.id && (
                  <div className="mt-4 rounded-xl bg-gray-50 p-4 dark:bg-gray-800/50">
                    <p className="mb-2 text-xs font-semibold text-gray-600 dark:text-gray-400">Live Test</p>
                    <TestPanel scraper={s} />
                  </div>
                )}

                {/* Edit form */}
                {editing?.id === s.id && (
                  <div className="mt-4 border-t border-gray-100 pt-4 dark:border-gray-800">
                    <ScraperForm
                      initial={editing}
                      onSave={handleUpdate}
                      onCancel={() => setEditing(null)}
                    />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
