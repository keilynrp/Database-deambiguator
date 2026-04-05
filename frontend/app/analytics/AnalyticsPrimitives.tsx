"use client";

import { Badge } from "../components/ui";

export function ProgressBar({
  value,
  max,
  color,
}: {
  value: number;
  max: number;
  color: string;
}) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  return (
    <div className="h-2 w-full rounded-full bg-gray-100 dark:bg-gray-800">
      <div className={`h-2 rounded-full transition-all duration-700 ${color}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export function SectionDivider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 py-2">
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-gray-700" />
      <span className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500">
        {label}
      </span>
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-gray-200 to-transparent dark:via-gray-700" />
    </div>
  );
}

const STATUS_VARIANT: Record<string, "success" | "warning" | "error" | "default"> = {
  completed: "success",
  pending: "warning",
  failed: "error",
  none: "default",
};

export function StatusBadge({ status, count }: { status: string; count: number }) {
  const variant = STATUS_VARIANT[status] ?? "default";
  return (
    <Badge variant={variant} dot dotPulse={status === "pending"} size="md">
      {status.charAt(0).toUpperCase() + status.slice(1)} · {count.toLocaleString()}
    </Badge>
  );
}

export function CitationBar({
  label,
  value,
  max,
}: {
  label: string;
  value: number;
  max: number;
}) {
  const pct = max > 0 ? (value / max) * 100 : 0;
  const gradients: Record<string, string> = {
    "0": "from-gray-400 to-gray-500",
    "1-10": "from-blue-400 to-blue-500",
    "11-50": "from-violet-400 to-violet-500",
    "51-200": "from-purple-500 to-fuchsia-500",
    "200+": "from-fuchsia-500 to-pink-500",
  };
  const grad = gradients[label] ?? "from-blue-400 to-blue-500";
  return (
    <div className="flex items-center gap-3">
      <span className="w-12 shrink-0 text-right text-xs font-medium text-gray-500 dark:text-gray-400">
        {label}
      </span>
      <div className="relative h-5 flex-1 overflow-hidden rounded-md bg-gray-100 dark:bg-gray-800">
        <div
          className={`h-full rounded-md bg-gradient-to-r ${grad} transition-all duration-700`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 shrink-0 text-xs font-semibold text-gray-700 dark:text-gray-300">{value}</span>
    </div>
  );
}

export function CoverageRing({ pct }: { pct: number }) {
  const r = 44;
  const circ = 2 * Math.PI * r;
  const offset = circ - (pct / 100) * circ;
  return (
    <div className="relative flex h-28 w-28 items-center justify-center">
      <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100">
        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          strokeWidth="10"
          className="stroke-gray-100 dark:stroke-gray-800"
        />
        <circle
          cx="50"
          cy="50"
          r={r}
          fill="none"
          strokeWidth="10"
          strokeLinecap="round"
          className="stroke-violet-500 transition-all duration-1000"
          strokeDasharray={circ}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="flex flex-col items-center">
        <span className="text-2xl font-bold text-gray-900 dark:text-white">{pct}%</span>
        <span className="text-[10px] font-medium uppercase tracking-wider text-gray-400 dark:text-gray-500">
          covered
        </span>
      </div>
    </div>
  );
}
