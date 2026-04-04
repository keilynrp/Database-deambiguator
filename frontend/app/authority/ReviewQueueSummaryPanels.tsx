"use client";

import type {
    AuthorMetrics,
    AuthorQueueSummary,
    QueueSummary,
} from "./reviewQueueTypes";

interface ReviewQueueSummaryPanelsProps {
    queueMode: "generic" | "authors";
    summary: QueueSummary | null;
    authorSummary: AuthorQueueSummary | null;
    authorMetrics: AuthorMetrics | null;
}

export default function ReviewQueueSummaryPanels({
    queueMode,
    summary,
    authorSummary,
    authorMetrics,
}: ReviewQueueSummaryPanelsProps) {
    return (
        <>
            {queueMode === "generic" && summary && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Pending Review</p>
                            <p className="mt-1 text-2xl font-bold text-amber-600 dark:text-amber-400">{summary.total_pending}</p>
                        </div>
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Confirmed</p>
                            <p className="mt-1 text-2xl font-bold text-green-600 dark:text-green-400">{summary.total_confirmed}</p>
                        </div>
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Rejected</p>
                            <p className="mt-1 text-2xl font-bold text-red-600 dark:text-red-400">{summary.total_rejected}</p>
                        </div>
                    </div>

                    {summary.by_field.length > 0 && (
                        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <div className="border-b border-gray-200 px-5 py-3 dark:border-gray-800">
                                <h3 className="text-sm font-medium text-gray-900 dark:text-white">By Field</h3>
                            </div>
                            <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                {summary.by_field.map(f => (
                                    <div key={f.field_name} className="flex items-center justify-between px-5 py-3">
                                        <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{f.field_name}</span>
                                        <div className="flex items-center gap-4 text-xs">
                                            <span className="text-amber-600">{f.pending} pending</span>
                                            <span className="text-green-600">{f.confirmed} confirmed</span>
                                            <span className="text-red-600">{f.rejected} rejected</span>
                                            <span className="text-gray-400">avg {(f.avg_confidence * 100).toFixed(0)}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}

            {queueMode === "authors" && authorSummary && (
                <>
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Author Records</p>
                            <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{authorSummary.total_records}</p>
                        </div>
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">Needs Review</p>
                            <p className="mt-1 text-2xl font-bold text-amber-600 dark:text-amber-400">{authorSummary.pending_review}</p>
                        </div>
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <p className="text-sm text-gray-500 dark:text-gray-400">NIL Cases</p>
                            <p className="mt-1 text-2xl font-bold text-rose-600 dark:text-rose-400">{authorSummary.nil_cases}</p>
                        </div>
                    </div>

                    {authorMetrics && (
                        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <div className="mb-4 flex items-center justify-between gap-3">
                                <h3 className="text-sm font-medium text-gray-900 dark:text-white">Engine Metrics</h3>
                                <span className="text-xs text-gray-400 dark:text-gray-500">author-only runtime</span>
                            </div>
                            <div className="grid grid-cols-2 gap-4 lg:grid-cols-5 xl:grid-cols-10">
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Avg confidence</p>
                                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                                        {(authorMetrics.avg_confidence * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Avg complexity</p>
                                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                                        {authorMetrics.avg_complexity.toFixed(2)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Avg NIL score</p>
                                    <p className="mt-1 text-lg font-semibold text-rose-600 dark:text-rose-400">
                                        {(authorMetrics.avg_nil_score * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Review rate</p>
                                    <p className="mt-1 text-lg font-semibold text-amber-600 dark:text-amber-400">
                                        {(authorMetrics.review_rate * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Confirm rate</p>
                                    <p className="mt-1 text-lg font-semibold text-green-600 dark:text-green-400">
                                        {(authorMetrics.confirm_rate * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">NIL rate</p>
                                    <p className="mt-1 text-lg font-semibold text-rose-600 dark:text-rose-400">
                                        {(authorMetrics.nil_rate * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Reformulations</p>
                                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                                        {authorMetrics.reformulation_attempts}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Applied</p>
                                    <p className="mt-1 text-lg font-semibold text-blue-600 dark:text-blue-400">
                                        {authorMetrics.reformulation_applied}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Apply rate</p>
                                    <p className="mt-1 text-lg font-semibold text-blue-600 dark:text-blue-400">
                                        {(authorMetrics.reformulation_apply_rate * 100).toFixed(0)}%
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Avg gain</p>
                                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                                        {authorMetrics.avg_reformulation_gain.toFixed(2)}
                                    </p>
                                </div>
                                <div>
                                    <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Est. cost</p>
                                    <p className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                                        ${authorMetrics.total_reformulation_cost.toFixed(4)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {authorMetrics && Object.keys(authorMetrics.by_nil_reason).length > 0 && (
                        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <div className="border-b border-gray-200 px-5 py-3 dark:border-gray-800">
                                <h3 className="text-sm font-medium text-gray-900 dark:text-white">NIL Reasons</h3>
                            </div>
                            <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                {Object.entries(authorMetrics.by_nil_reason).map(([reason, count]) => (
                                    <div key={reason} className="flex items-center justify-between px-5 py-3">
                                        <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{reason}</span>
                                        <span className="text-xs text-gray-500 dark:text-gray-400">{count} records</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {Object.keys(authorSummary.by_route).length > 0 && (
                        <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                            <div className="border-b border-gray-200 px-5 py-3 dark:border-gray-800">
                                <h3 className="text-sm font-medium text-gray-900 dark:text-white">By Route</h3>
                            </div>
                            <div className="divide-y divide-gray-100 dark:divide-gray-800">
                                {Object.entries(authorSummary.by_route).map(([routeKey, count]) => (
                                    <div key={routeKey} className="flex items-center justify-between px-5 py-3">
                                        <span className="text-sm font-mono text-gray-700 dark:text-gray-300">{routeKey}</span>
                                        <span className="text-xs text-gray-500 dark:text-gray-400">{count} records</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}
        </>
    );
}
