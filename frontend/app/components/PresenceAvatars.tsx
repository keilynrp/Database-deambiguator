/**
 * Sprint 91 — PresenceAvatars component.
 *
 * Shows who else is in the same WebSocket room as colored avatar circles
 * with initials. A pulsing green dot indicates the live connection.
 *
 * Props:
 *   presence     — list of PresenceUser from useWebSocket()
 *   isConnected  — whether the WS is currently OPEN
 *   maxVisible   — max avatars before "+N" overflow badge (default 5)
 *   className    — extra Tailwind classes
 */
"use client";

import type { PresenceUser } from "@/lib/useWebSocket";

// Tailwind colour ring + bg pairs — one per user slot (cycles)
const AVATAR_COLORS = [
  "bg-violet-500 ring-violet-300 dark:ring-violet-700",
  "bg-blue-500   ring-blue-300   dark:ring-blue-700",
  "bg-emerald-500 ring-emerald-300 dark:ring-emerald-700",
  "bg-amber-500  ring-amber-300   dark:ring-amber-700",
  "bg-rose-500   ring-rose-300   dark:ring-rose-700",
];

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

interface Props {
  presence: PresenceUser[];
  isConnected: boolean;
  maxVisible?: number;
  className?: string;
}

export default function PresenceAvatars({
  presence,
  isConnected,
  maxVisible = 5,
  className = "",
}: Props) {
  if (!isConnected && presence.length === 0) return null;

  const visible = presence.slice(0, maxVisible);
  const overflow = presence.length - maxVisible;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {/* Live indicator dot */}
      <span
        className={`h-2 w-2 rounded-full ${
          isConnected
            ? "bg-emerald-400 animate-pulse"
            : "bg-gray-300 dark:bg-gray-600"
        }`}
        title={isConnected ? "Connected" : "Reconnecting…"}
      />

      {/* Avatar stack */}
      {visible.length > 0 && (
        <div className="flex -space-x-2">
          {visible.map((user, i) => (
            <div
              key={user.user_id}
              title={`${user.display_name || user.username} is here`}
              className={`
                flex h-7 w-7 items-center justify-center rounded-full
                ring-2 ring-white dark:ring-gray-900
                text-[10px] font-bold text-white select-none
                ${AVATAR_COLORS[i % AVATAR_COLORS.length]}
              `}
            >
              {initials(user.display_name || user.username)}
            </div>
          ))}

          {overflow > 0 && (
            <div
              className="
                flex h-7 w-7 items-center justify-center rounded-full
                ring-2 ring-white dark:ring-gray-900
                bg-gray-200 dark:bg-gray-700
                text-[10px] font-bold text-gray-600 dark:text-gray-300
              "
              title={`${overflow} more user${overflow > 1 ? "s" : ""}`}
            >
              +{overflow}
            </div>
          )}
        </div>
      )}

      {/* Count label */}
      <span className="text-xs text-gray-400 dark:text-gray-500 tabular-nums">
        {presence.length === 0
          ? "only you"
          : presence.length === 1
          ? "1 online"
          : `${presence.length} online`}
      </span>
    </div>
  );
}
