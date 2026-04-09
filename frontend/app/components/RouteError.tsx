"use client";

// Shared component used by route-level error.tsx files.
// Renders an inline error card with retry + home actions.

import Link from "next/link";

interface RouteErrorProps {
  title?: string;
  error: Error & { digest?: string };
  reset: () => void;
}

export default function RouteError({
  title = "Failed to load this page",
  error,
  reset,
}: RouteErrorProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center py-24 px-4">
      <div className="w-full max-w-sm text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-500 dark:bg-red-900/30 dark:text-red-400">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 9v2m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
          </svg>
        </div>

        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">{title}</h2>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {error.message || "An unexpected error occurred."}
        </p>
        {error.digest && (
          <p className="mt-2 font-mono text-xs text-gray-400 dark:text-gray-600">ID: {error.digest}</p>
        )}

        <div className="mt-6 flex justify-center gap-3">
          <button
            onClick={reset}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            Try again
          </button>
          <Link
            href="/"
            className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors dark:border-gray-700 dark:bg-transparent dark:text-gray-300 dark:hover:bg-gray-800"
          >
            Home
          </Link>
        </div>
      </div>
    </div>
  );
}
