"use client";

// ── Unified Error Banner ───────────────────────────────────────────────────
// Used for inline section errors (fetch failures, API errors).
// Works both as a standalone block and inside a table <td>.
// Replaces all console.error()-only error handling across the app.

type ErrorBannerVariant = "inline" | "card" | "row";

interface ErrorBannerProps {
  message: string;
  detail?: string;
  onRetry?: () => void;
  /** "inline" = slim bar, "card" = padded card, "row" = centered block (for tables) */
  variant?: ErrorBannerVariant;
  className?: string;
}

export default function ErrorBanner({
  message,
  detail,
  onRetry,
  variant = "card",
  className = "",
}: ErrorBannerProps) {
  if (variant === "inline") {
    return (
      <div
        role="alert"
        className={`flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 px-4 py-3 dark:border-red-800/50 dark:bg-red-900/10 ${className}`}
      >
        <svg
          className="h-4 w-4 shrink-0 text-red-500 dark:text-red-400"
          fill="none" stroke="currentColor" viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
        </svg>
        <p className="flex-1 text-sm font-medium text-red-700 dark:text-red-300">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="shrink-0 rounded px-2.5 py-1 text-xs font-semibold text-red-700 ring-1 ring-red-300 hover:bg-red-100 transition-colors dark:text-red-300 dark:ring-red-700 dark:hover:bg-red-900/30"
          >
            Retry
          </button>
        )}
      </div>
    );
  }

  if (variant === "row") {
    // Intended for use inside a <tbody> — caller wraps in <tr><td colSpan={n}>
    return (
      <div className={`flex flex-col items-center gap-3 py-10 ${className}`} role="alert">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-500 dark:bg-red-900/30 dark:text-red-400">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <div className="text-center">
          <p className="text-sm font-semibold text-gray-800 dark:text-gray-200">{message}</p>
          {detail && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{detail}</p>}
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="rounded-lg border border-red-200 bg-red-50 px-4 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-100 transition-colors dark:border-red-800 dark:bg-red-900/20 dark:text-red-300 dark:hover:bg-red-900/40"
          >
            Try again
          </button>
        )}
      </div>
    );
  }

  // Default: "card"
  return (
    <div
      role="alert"
      className={`rounded-xl border border-red-200 bg-red-50 p-5 dark:border-red-800/50 dark:bg-red-900/10 ${className}`}
    >
      <div className="flex gap-3">
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400">
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-red-800 dark:text-red-300">{message}</p>
          {detail && (
            <p className="mt-0.5 text-xs text-red-600/80 dark:text-red-400/80 font-mono break-all">{detail}</p>
          )}
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 inline-flex items-center gap-1.5 rounded-lg border border-red-300 bg-white px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-50 transition-colors dark:border-red-700 dark:bg-transparent dark:text-red-300 dark:hover:bg-red-900/30"
            >
              <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
