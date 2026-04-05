"use client";

import { SnapshotCards } from "./ContextPanels";
import type { Snapshot } from "./contextTypes";

export function SnapshotTab({
  snapshot,
  loading,
  error,
  saveLabel,
  saving,
  onSaveLabelChange,
  onSave,
  onRefresh,
}: {
  snapshot: Snapshot | null;
  loading: boolean;
  error: string | null;
  saveLabel: string;
  saving: boolean;
  onSaveLabelChange: (value: string) => void;
  onSave: () => void;
  onRefresh: () => void;
}) {
  return (
    <div className="space-y-4">
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}
      {loading && !snapshot && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[1, 2, 3].map((item) => (
            <div key={item} className="h-24 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />
          ))}
        </div>
      )}
      {snapshot && (
        <>
          <SnapshotCards snap={snapshot} />
          <div className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900">
            <input
              type="text"
              value={saveLabel}
              onChange={(e) => onSaveLabelChange(e.target.value)}
              placeholder="Session label (optional)..."
              className="flex-1 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-blue-500 focus:outline-none dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500"
            />
            <button
              type="button"
              onClick={onSave}
              disabled={saving}
              className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save to Memory"}
            </button>
            <button
              type="button"
              onClick={onRefresh}
              disabled={loading}
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
  );
}
