"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { apiFetch } from "@/lib/api";
import { WIDGET_REGISTRY, type WidgetConfig } from "./widgets";
import PresenceAvatars from "../components/PresenceAvatars";
import { useWebSocket } from "@/lib/useWebSocket";

// ── Types ─────────────────────────────────────────────────────────────────────

interface Dashboard {
  id: number;
  name: string;
  layout: WidgetConfig[];
  is_default: boolean;
  updated_at: string | null;
}

interface WidgetType {
  type: string;
  label: string;
  description: string;
  default_cols: number;
  icon: string;
}

// ── Icon helper ───────────────────────────────────────────────────────────────

function WidgetIcon({ icon }: { icon: string }) {
  const paths: Record<string, string> = {
    "chart-bar":         "M3 3v18h18M7 16l4-4 4 4 5-5",
    "beaker":            "M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.3 24.3 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15M14.25 3.104c.251.023.501.05.75.082M19.8 15a2.25 2.25 0 010 3.182M19.8 15l-2.8-2.8M5 14.5a2.25 2.25 0 000 3.182M5 14.5l2.8-2.8m0 0L12 7.5m-4.2 4.2L12 7.5m5 4.2L12 7.5",
    "table-cells":       "M3 3h18v18H3V3zm6 0v18M15 3v18M3 9h18M3 15h18",
    "tag":               "M9.568 3H5.25A2.25 2.25 0 003 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 005.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 009.568 3z",
    "sparkles":          "M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456z",
    "clock":             "M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z",
    "chart-bar-square":  "M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z",
    "cube":              "M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9",
  };
  return (
    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={paths[icon] ?? paths["chart-bar"]} />
    </svg>
  );
}

// ── Unique ID generator ───────────────────────────────────────────────────────

let _seq = 0;
function uid() { return `w_${Date.now()}_${++_seq}`; }

// ── Widget Picker Modal ───────────────────────────────────────────────────────

function WidgetPicker({
  catalogue,
  onAdd,
  onClose,
}: {
  catalogue: WidgetType[];
  onAdd: (wt: WidgetType) => void;
  onClose: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-xl rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-900">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">Add Widget</h3>
          <button onClick={onClose} className="rounded p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {catalogue.map((wt) => (
            <button
              key={wt.type}
              onClick={() => { onAdd(wt); onClose(); }}
              className="flex items-start gap-3 rounded-xl border border-gray-200 p-3 text-left hover:border-blue-400 hover:bg-blue-50 dark:border-gray-700 dark:hover:border-blue-600 dark:hover:bg-blue-900/20"
            >
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                <WidgetIcon icon={wt.icon} />
              </span>
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{wt.label}</p>
                <p className="mt-0.5 text-xs text-gray-500 dark:text-gray-400">{wt.description}</p>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Dashboard Grid ────────────────────────────────────────────────────────────

const COL_CLASS: Record<number, string> = {
  4:  "col-span-4",
  6:  "col-span-6",
  8:  "col-span-8",
  12: "col-span-12",
};

function DashboardGrid({
  widgets,
  editing,
  onReorder,
  onRemove,
}: {
  widgets: WidgetConfig[];
  editing: boolean;
  onReorder: (from: number, to: number) => void;
  onRemove: (id: string) => void;
}) {
  const dragIdx = useRef<number | null>(null);

  function handleDragStart(e: React.DragEvent, idx: number) {
    dragIdx.current = idx;
    e.dataTransfer.effectAllowed = "move";
  }

  function handleDrop(e: React.DragEvent, toIdx: number) {
    e.preventDefault();
    if (dragIdx.current !== null && dragIdx.current !== toIdx) {
      onReorder(dragIdx.current, toIdx);
    }
    dragIdx.current = null;
  }

  function handleDragOver(e: React.DragEvent) {
    e.preventDefault();
    e.dataTransfer.dropEffect = "move";
  }

  if (widgets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-200 py-24 dark:border-gray-700">
        <svg className="mb-3 h-10 w-10 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
        </svg>
        <p className="text-sm text-gray-400 dark:text-gray-500">
          {editing ? "Click \"+ Add Widget\" to build your dashboard" : "This dashboard is empty."}
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-12 gap-4">
      {widgets.map((w, idx) => {
        const Renderer = WIDGET_REGISTRY[w.type];
        const spanClass = COL_CLASS[w.cols] ?? "col-span-6";
        return (
          <div
            key={w.id}
            className={`${spanClass} relative rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-900 ${editing ? "cursor-grab active:cursor-grabbing" : ""}`}
            style={{ minHeight: 200 }}
            draggable={editing}
            onDragStart={(e) => editing && handleDragStart(e, idx)}
            onDragOver={handleDragOver}
            onDrop={(e) => editing && handleDrop(e, idx)}
          >
            {editing && (
              <div className="absolute right-2 top-2 flex items-center gap-1">
                {/* Drag handle hint */}
                <span className="cursor-grab text-gray-300 dark:text-gray-600" title="Drag to reorder">
                  <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="9" cy="6"  r="1.5" /><circle cx="15" cy="6"  r="1.5" />
                    <circle cx="9" cy="12" r="1.5" /><circle cx="15" cy="12" r="1.5" />
                    <circle cx="9" cy="18" r="1.5" /><circle cx="15" cy="18" r="1.5" />
                  </svg>
                </span>
                <button
                  onClick={() => onRemove(w.id)}
                  title="Remove widget"
                  className="rounded p-0.5 text-gray-300 hover:text-red-500 dark:text-gray-600 dark:hover:text-red-400"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            )}
            {Renderer ? (
              <Renderer config={w} />
            ) : (
              <p className="text-xs text-red-400">Unknown widget type: {w.type}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function DashboardsPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [catalogue, setCatalogue]   = useState<WidgetType[]>([]);
  const [activeDash, setActiveDash] = useState<Dashboard | null>(null);

  // Real-time presence (Sprint 91)
  const { presence, isConnected } = useWebSocket(
    activeDash ? `dashboard-${activeDash.id}` : null
  );
  const [editLayout, setEditLayout] = useState<WidgetConfig[]>([]);
  const [editing, setEditing]       = useState(false);
  const [loading, setLoading]       = useState(true);
  const [saving, setSaving]         = useState(false);
  const [showPicker, setShowPicker] = useState(false);
  const [showNewForm, setShowNewForm] = useState(false);
  const [newName, setNewName]       = useState("");
  const [creatingNew, setCreatingNew] = useState(false);

  // ── Load ──────────────────────────────────────────────────────────────────

  const load = useCallback(async () => {
    setLoading(true);
    const [dRes, cRes] = await Promise.all([
      apiFetch("/dashboards"),
      apiFetch("/dashboards/widget-types"),
    ]);
    const dashes: Dashboard[] = dRes.ok ? await dRes.json() : [];
    const cat: WidgetType[]   = cRes.ok ? await cRes.json() : [];
    setCatalogue(cat);
    setDashboards(dashes);
    // Select default or first
    const def = dashes.find((d) => d.is_default) ?? dashes[0] ?? null;
    if (def) {
      setActiveDash(def);
      setEditLayout(def.layout);
    }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  // ── Dashboard selection ───────────────────────────────────────────────────

  function selectDash(d: Dashboard) {
    if (editing) {
      if (!confirm("Discard unsaved changes?")) return;
      setEditing(false);
    }
    setActiveDash(d);
    setEditLayout(d.layout);
  }

  // ── Editing ───────────────────────────────────────────────────────────────

  function startEdit() {
    setEditLayout(activeDash?.layout ?? []);
    setEditing(true);
  }

  function cancelEdit() {
    setEditLayout(activeDash?.layout ?? []);
    setEditing(false);
  }

  async function saveEdit() {
    if (!activeDash) return;
    setSaving(true);
    const res = await apiFetch(`/dashboards/${activeDash.id}`, {
      method: "PUT",
      body: JSON.stringify({ layout: editLayout }),
    });
    if (res.ok) {
      const updated: Dashboard = await res.json();
      setActiveDash(updated);
      setDashboards((prev) => prev.map((d) => d.id === updated.id ? updated : d));
      setEditing(false);
    }
    setSaving(false);
  }

  // ── Widget CRUD ───────────────────────────────────────────────────────────

  function addWidget(wt: WidgetType) {
    const w: WidgetConfig = {
      id:    uid(),
      type:  wt.type,
      title: wt.label,
      cols:  wt.default_cols,
      config: {},
    };
    setEditLayout((prev) => [...prev, w]);
  }

  function removeWidget(id: string) {
    setEditLayout((prev) => prev.filter((w) => w.id !== id));
  }

  function reorderWidgets(from: number, to: number) {
    setEditLayout((prev) => {
      const next = [...prev];
      const [item] = next.splice(from, 1);
      next.splice(to, 0, item);
      return next;
    });
  }

  // ── New dashboard ─────────────────────────────────────────────────────────

  async function createDashboard() {
    if (!newName.trim()) return;
    setCreatingNew(true);
    const res = await apiFetch("/dashboards", {
      method: "POST",
      body: JSON.stringify({ name: newName.trim(), layout: [] }),
    });
    if (res.ok) {
      const created: Dashboard = await res.json();
      setDashboards((prev) => [created, ...prev]);
      setActiveDash(created);
      setEditLayout([]);
      setShowNewForm(false);
      setNewName("");
      setEditing(true);
    }
    setCreatingNew(false);
  }

  // ── Set default ───────────────────────────────────────────────────────────

  async function setDefault(d: Dashboard) {
    const res = await apiFetch(`/dashboards/${d.id}/default`, { method: "POST" });
    if (res.ok) {
      const updated: Dashboard = await res.json();
      setDashboards((prev) =>
        prev.map((x) => ({ ...x, is_default: x.id === updated.id }))
      );
      setActiveDash(updated);
    }
  }

  // ── Delete dashboard ──────────────────────────────────────────────────────

  async function deleteDash(d: Dashboard) {
    if (!confirm(`Delete dashboard "${d.name}"?`)) return;
    await apiFetch(`/dashboards/${d.id}`, { method: "DELETE" });
    await load();
  }

  // ── Render ────────────────────────────────────────────────────────────────

  const displayWidgets = editing ? editLayout : (activeDash?.layout ?? []);

  return (
    <div className="flex h-full min-h-screen">
      {/* Sidebar — dashboard list */}
      <aside className="w-64 shrink-0 border-r border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900/60 flex flex-col">
        <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-700">
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">My Dashboards</span>
          <button
            onClick={() => setShowNewForm(true)}
            title="New dashboard"
            className="rounded-lg p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-700 dark:hover:bg-gray-700 dark:hover:text-gray-200"
          >
            <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
        </div>

        {loading ? (
          <div className="p-4 space-y-2">
            {[1, 2, 3].map((i) => <div key={i} className="h-10 animate-pulse rounded-lg bg-gray-200 dark:bg-gray-700" />)}
          </div>
        ) : (
          <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {dashboards.length === 0 && (
              <p className="px-3 py-6 text-center text-xs text-gray-400">No dashboards yet.</p>
            )}
            {dashboards.map((d) => (
              <button
                key={d.id}
                onClick={() => selectDash(d)}
                className={`group w-full flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                  activeDash?.id === d.id
                    ? "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300"
                    : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                }`}
              >
                <span className="flex-1 truncate">{d.name}</span>
                {d.is_default && (
                  <span className="rounded px-1 text-[9px] font-bold uppercase bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">
                    default
                  </span>
                )}
                {/* Actions visible on hover */}
                <span className="hidden group-hover:flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                  {!d.is_default && (
                    <span
                      onClick={() => setDefault(d)}
                      title="Set as default"
                      className="cursor-pointer text-gray-400 hover:text-amber-500"
                    >
                      <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                      </svg>
                    </span>
                  )}
                  <span
                    onClick={() => deleteDash(d)}
                    title="Delete"
                    className="cursor-pointer text-gray-400 hover:text-red-500"
                  >
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </span>
                </span>
              </button>
            ))}
          </nav>
        )}

        {/* New dashboard form */}
        {showNewForm && (
          <div className="border-t border-gray-200 p-3 dark:border-gray-700">
            <input
              autoFocus
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") createDashboard(); if (e.key === "Escape") setShowNewForm(false); }}
              placeholder="Dashboard name…"
              className="w-full rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-sm text-gray-800 outline-none focus:border-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
            />
            <div className="mt-2 flex gap-2">
              <button
                onClick={createDashboard}
                disabled={creatingNew || !newName.trim()}
                className="flex-1 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {creatingNew ? "Creating…" : "Create"}
              </button>
              <button
                onClick={() => { setShowNewForm(false); setNewName(""); }}
                className="rounded-lg border border-gray-200 px-3 py-1.5 text-xs text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Main canvas */}
      <main className="flex-1 overflow-y-auto p-6 space-y-5">
        {activeDash ? (
          <>
            {/* Toolbar */}
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">{activeDash.name}</h2>
                <p className="text-xs text-gray-400">
                  {displayWidgets.length} widget{displayWidgets.length !== 1 ? "s" : ""}
                  {activeDash.updated_at && ` · saved ${new Date(activeDash.updated_at).toLocaleDateString()}`}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <PresenceAvatars presence={presence} isConnected={isConnected} />
                {editing ? (
                  <>
                    <button
                      onClick={() => setShowPicker(true)}
                      className="flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                    >
                      <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                      Add Widget
                    </button>
                    <button
                      onClick={cancelEdit}
                      className="rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 dark:border-gray-700 dark:text-gray-400"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={saveEdit}
                      disabled={saving}
                      className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                    >
                      {saving ? "Saving…" : "Save"}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={startEdit}
                    className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
                  >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    Edit Dashboard
                  </button>
                )}
              </div>
            </div>

            {editing && (
              <div className="flex items-center gap-2 rounded-lg bg-blue-50 px-4 py-2.5 text-sm text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
                <svg className="h-4 w-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Edit mode — drag widgets to reorder, click × to remove. Click Save when done.
              </div>
            )}

            <DashboardGrid
              widgets={displayWidgets}
              editing={editing}
              onReorder={reorderWidgets}
              onRemove={removeWidget}
            />
          </>
        ) : (
          !loading && (
            <div className="flex flex-col items-center justify-center py-32">
              <svg className="mb-4 h-14 w-14 text-gray-200 dark:text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
              </svg>
              <p className="mb-2 text-lg font-semibold text-gray-400 dark:text-gray-500">No dashboards yet</p>
              <p className="mb-6 text-sm text-gray-400">Create your first personalised dashboard to get started.</p>
              <button
                onClick={() => setShowNewForm(true)}
                className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700"
              >
                Create Dashboard
              </button>
            </div>
          )
        )}
      </main>

      {/* Widget picker modal */}
      {showPicker && (
        <WidgetPicker
          catalogue={catalogue}
          onAdd={addWidget}
          onClose={() => setShowPicker(false)}
        />
      )}
    </div>
  );
}
