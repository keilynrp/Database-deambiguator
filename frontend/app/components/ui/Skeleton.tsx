"use client";

// ── Unified Skeleton System ────────────────────────────────────────────────
// All loading states in UKIP use these components for visual consistency.
// Every skeleton uses Tailwind's animate-pulse with a neutral shimmer tone
// that works correctly in both light and dark modes.

const base = "rounded bg-gray-200 dark:bg-gray-700 animate-pulse";

// ── Primitives ─────────────────────────────────────────────────────────────

export function SkeletonText({
  width = "100%",
  height = "h-4",
  className = "",
}: {
  width?: string | number;
  height?: string;
  className?: string;
}) {
  const w = typeof width === "number" ? `${width}px` : width;
  return (
    <div
      className={`${base} ${height} ${className}`}
      style={{ width: w }}
      aria-hidden="true"
    />
  );
}

export function SkeletonAvatar({ size = "h-8 w-8" }: { size?: string }) {
  return (
    <div
      className={`${base} rounded-full shrink-0 ${size}`}
      aria-hidden="true"
    />
  );
}

export function SkeletonBadge() {
  return (
    <div
      className={`${base} h-5 w-16 rounded-full`}
      aria-hidden="true"
    />
  );
}

// ── Table skeleton ─────────────────────────────────────────────────────────

interface SkeletonRowProps {
  cols?: number;
  /** Column widths as Tailwind width classes, e.g. ["w-8","w-48","w-24"] */
  colWidths?: string[];
}

export function SkeletonRow({ cols = 6, colWidths }: SkeletonRowProps) {
  return (
    <tr aria-hidden="true" className="border-b border-gray-100 dark:border-gray-800">
      {Array.from({ length: cols }).map((_, i) => (
        <td key={i} className="px-5 py-4">
          <div
            className={`${base} h-3.5 rounded ${colWidths?.[i] ?? ""}`}
            style={!colWidths?.[i] ? { width: `${55 + ((i * 37) % 40)}%` } : undefined}
          />
        </td>
      ))}
    </tr>
  );
}

export function SkeletonTableBody({
  rows = 8,
  cols = 6,
  colWidths,
}: {
  rows?: number;
  cols?: number;
  colWidths?: string[];
}) {
  return (
    <>
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonRow key={i} cols={cols} colWidths={colWidths} />
      ))}
    </>
  );
}

// ── Card skeleton ──────────────────────────────────────────────────────────

export function SkeletonCard({ lines = 3 }: { lines?: number }) {
  return (
    <div
      className="rounded-xl border border-gray-200 bg-white p-5 space-y-3 dark:border-gray-800 dark:bg-gray-900"
      aria-hidden="true"
    >
      <SkeletonText height="h-4" width="60%" />
      {Array.from({ length: lines }).map((_, i) => (
        <SkeletonText key={i} height="h-3" width={`${90 - i * 12}%`} />
      ))}
    </div>
  );
}

export function SkeletonCardGrid({ count = 4, lines = 3 }: { count?: number; lines?: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-hidden="true">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} lines={lines} />
      ))}
    </div>
  );
}

// ── Stat card skeleton (mirrors StatCard layout) ───────────────────────────

export function SkeletonStatCard() {
  return (
    <div
      className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-800 dark:bg-gray-900"
      aria-hidden="true"
    >
      <div className="flex items-center justify-between">
        <div className={`${base} h-9 w-9 rounded-lg`} />
        <div className={`${base} h-3.5 w-12 rounded`} />
      </div>
      <div className="mt-4 space-y-1.5">
        <div className={`${base} h-6 w-24 rounded`} />
        <div className={`${base} h-3 w-32 rounded`} />
      </div>
    </div>
  );
}

// ── List item skeleton ─────────────────────────────────────────────────────

export function SkeletonListItem() {
  return (
    <div
      className="flex items-center gap-3 px-5 py-3.5 border-b border-gray-100 dark:border-gray-800"
      aria-hidden="true"
    >
      <SkeletonAvatar size="h-7 w-7" />
      <div className="flex-1 space-y-1.5">
        <SkeletonText height="h-3.5" width="55%" />
        <SkeletonText height="h-3" width="75%" />
      </div>
    </div>
  );
}

export function SkeletonList({ rows = 5 }: { rows?: number }) {
  return (
    <div aria-hidden="true">
      {Array.from({ length: rows }).map((_, i) => (
        <SkeletonListItem key={i} />
      ))}
    </div>
  );
}
