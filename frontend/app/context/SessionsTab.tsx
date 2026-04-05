"use client";

import { SnapshotCards } from "./ContextPanels";
import type { Session, SessionDetail } from "./contextTypes";

export function SessionsTab({
  loadingSessions,
  sessions,
  sortedSessions,
  selectedSession,
  loadingDetail,
  editingNotes,
  savingNotes,
  sessionInsights,
  loadingInsights,
  insightsError,
  onFetchDetail,
  onFetchInsights,
  onDeleteSession,
  onPatchSession,
  onEditingNotesChange,
}: {
  loadingSessions: boolean;
  sessions: Session[];
  sortedSessions: Session[];
  selectedSession: SessionDetail | null;
  loadingDetail: boolean;
  editingNotes: Record<number, string>;
  savingNotes: Record<number, boolean>;
  sessionInsights: Record<number, string>;
  loadingInsights: Record<number, boolean>;
  insightsError: string | null;
  onFetchDetail: (id: number) => void;
  onFetchInsights: (id: number) => void;
  onDeleteSession: (id: number) => void;
  onPatchSession: (id: number, patch: { label?: string; notes?: string; pinned?: boolean }) => void;
  onEditingNotesChange: (id: number, value: string) => void;
}) {
  return (
    <div className="grid gap-4 xl:grid-cols-[1fr_380px]">
      <div className="space-y-3">
        {loadingSessions && (
          <div className="space-y-3">
            {[1, 2, 3].map((item) => (
              <div key={item} className="h-16 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />
            ))}
          </div>
        )}
        {!loadingSessions && sessions.length === 0 && (
          <div className="flex flex-col items-center py-16 text-center">
            <span className="text-4xl">💾</span>
            <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
              No saved sessions yet. Capture a snapshot from the Live Snapshot tab.
            </p>
          </div>
        )}
        {sortedSessions.map((session) => (
          <div
            key={session.id}
            className={`rounded-xl border bg-white px-5 py-4 shadow-sm dark:bg-gray-900 ${
              selectedSession?.id === session.id
                ? "border-blue-400 dark:border-blue-600"
                : "border-gray-200 dark:border-gray-700"
            }`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onPatchSession(session.id, { pinned: !session.pinned })}
                    title={session.pinned ? "Unpin" : "Pin"}
                    className={`text-lg leading-none ${
                      session.pinned ? "text-amber-400" : "text-gray-300 hover:text-amber-300"
                    }`}
                  >
                    {session.pinned ? "★" : "☆"}
                  </button>
                  <p className="truncate text-sm font-medium text-gray-900 dark:text-white">
                    {session.label || `Snapshot #${session.id}`}
                  </p>
                </div>
                <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500">
                  Domain: <span className="font-medium">{session.domain_id}</span> ·{" "}
                  {new Date(session.created_at).toLocaleString()}
                </p>
              </div>
              <div className="flex shrink-0 gap-2">
                <button
                  type="button"
                  onClick={() => onFetchDetail(session.id)}
                  className="rounded-lg border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-medium text-blue-700 hover:bg-blue-100 dark:border-blue-800 dark:bg-blue-900/10 dark:text-blue-400"
                >
                  Details
                </button>
                <button
                  type="button"
                  onClick={() => onFetchInsights(session.id)}
                  disabled={loadingInsights[session.id]}
                  className="rounded-lg border border-violet-200 bg-violet-50 px-3 py-1.5 text-xs font-medium text-violet-700 hover:bg-violet-100 disabled:opacity-50 dark:border-violet-800 dark:bg-violet-900/10 dark:text-violet-400"
                >
                  {loadingInsights[session.id] ? "..." : "AI Insights"}
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteSession(session.id)}
                  className="rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100 dark:border-red-800 dark:bg-red-900/10 dark:text-red-400"
                >
                  Delete
                </button>
              </div>
            </div>

            <div className="mt-3 flex gap-2">
              <textarea
                rows={2}
                value={editingNotes[session.id] ?? session.notes ?? ""}
                onChange={(e) => onEditingNotesChange(session.id, e.target.value)}
                placeholder="Add notes..."
                className="flex-1 resize-none rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-700 focus:border-blue-400 focus:outline-none dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
              />
              <button
                type="button"
                disabled={savingNotes[session.id]}
                onClick={() =>
                  onPatchSession(session.id, {
                    notes: editingNotes[session.id] ?? session.notes ?? "",
                  })
                }
                className="self-end rounded-lg bg-gray-100 px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-200 disabled:opacity-50 dark:bg-gray-700 dark:text-gray-300"
              >
                {savingNotes[session.id] ? "..." : "Save"}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="space-y-4">
        <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-800/50">
          {loadingDetail && <div className="h-48 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-700" />}
          {!loadingDetail && !selectedSession && (
            <p className="py-12 text-center text-sm text-gray-400 dark:text-gray-500">
              Select a session to view details
            </p>
          )}
          {selectedSession && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <p className="truncate text-sm font-semibold text-gray-900 dark:text-white">
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

        {selectedSession && sessionInsights[selectedSession.id] && (
          <div className="rounded-2xl border border-violet-200 bg-violet-50 p-4 dark:border-violet-800 dark:bg-violet-500/5">
            <p className="mb-2 text-xs font-semibold text-violet-700 dark:text-violet-300">AI Insights</p>
            <p className="whitespace-pre-wrap text-xs leading-relaxed text-violet-900 dark:text-violet-200">
              {sessionInsights[selectedSession.id]}
            </p>
          </div>
        )}

        {insightsError && (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-700 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-300">
            {insightsError}
          </div>
        )}
      </div>
    </div>
  );
}
