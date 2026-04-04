"use client";

import type { DomainAttribute, DomainSchema } from "../contexts/DomainContext";
import type { QueueSummary } from "./reviewQueueTypes";

interface ReviewQueueControlsProps {
    activeDomain: DomainSchema | null;
    queueMode: "generic" | "authors";
    statusFilter: string;
    fieldFilter: string;
    authorRouteFilter: string;
    authorReviewFilter: string;
    authorNilOnly: boolean;
    batchField: string;
    batchEntityType: string;
    batchLimit: number;
    resolving: boolean;
    resolveResult: string | null;
    acting: boolean;
    selectedCount: number;
    summary: QueueSummary | null;
    onQueueModeChange: (mode: "generic" | "authors") => void;
    onStatusFilterChange: (value: string) => void;
    onFieldFilterChange: (value: string) => void;
    onAuthorRouteFilterChange: (value: string) => void;
    onAuthorReviewFilterChange: (value: string) => void;
    onAuthorNilOnlyChange: (value: boolean) => void;
    onBatchFieldChange: (value: string) => void;
    onBatchEntityTypeChange: (value: string) => void;
    onBatchLimitChange: (value: number) => void;
    onBatchResolve: () => void;
    onBulkAction: (action: "bulk-confirm" | "bulk-reject") => void;
}

export default function ReviewQueueControls({
    activeDomain,
    queueMode,
    statusFilter,
    fieldFilter,
    authorRouteFilter,
    authorReviewFilter,
    authorNilOnly,
    batchField,
    batchEntityType,
    batchLimit,
    resolving,
    resolveResult,
    acting,
    selectedCount,
    summary,
    onQueueModeChange,
    onStatusFilterChange,
    onFieldFilterChange,
    onAuthorRouteFilterChange,
    onAuthorReviewFilterChange,
    onAuthorNilOnlyChange,
    onBatchFieldChange,
    onBatchEntityTypeChange,
    onBatchLimitChange,
    onBatchResolve,
    onBulkAction,
}: ReviewQueueControlsProps) {
    return (
        <>
            <div className="inline-flex rounded-xl border border-gray-200 bg-white p-1 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <button
                    onClick={() => onQueueModeChange("generic")}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                        queueMode === "generic"
                            ? "bg-blue-600 text-white"
                            : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    }`}
                >
                    Generic Queue
                </button>
                <button
                    onClick={() => onQueueModeChange("authors")}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                        queueMode === "authors"
                            ? "bg-blue-600 text-white"
                            : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    }`}
                >
                    Author Queue
                </button>
            </div>

            {queueMode === "generic" && (
                <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                    <h3 className="mb-3 text-sm font-medium text-gray-900 dark:text-white">Batch Resolve</h3>
                    <div className="flex flex-wrap items-end gap-4">
                        <div className="min-w-[160px]">
                            <label className="mb-1 block text-xs text-gray-500 dark:text-gray-400">Field</label>
                            <select
                                value={batchField}
                                onChange={e => onBatchFieldChange(e.target.value)}
                                className="h-9 w-full rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                            >
                                {activeDomain ? (
                                    activeDomain.attributes
                                        .filter((a: DomainAttribute) => a.type === "string")
                                        .map((attr: DomainAttribute) => (
                                            <option key={attr.name} value={attr.name}>{attr.label}</option>
                                        ))
                                ) : (
                                    <option value="">Loading...</option>
                                )}
                            </select>
                        </div>
                        <div className="min-w-[130px]">
                            <label className="mb-1 block text-xs text-gray-500 dark:text-gray-400">Entity Type</label>
                            <select
                                value={batchEntityType}
                                onChange={e => onBatchEntityTypeChange(e.target.value)}
                                className="h-9 w-full rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                            >
                                {["general", "person", "organization", "concept", "institution"].map(et => (
                                    <option key={et} value={et}>{et}</option>
                                ))}
                            </select>
                        </div>
                        <div className="w-20">
                            <label className="mb-1 block text-xs text-gray-500 dark:text-gray-400">Limit</label>
                            <input
                                type="number"
                                min={1}
                                max={100}
                                value={batchLimit}
                                onChange={e => onBatchLimitChange(Number(e.target.value))}
                                className="h-9 w-full rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                            />
                        </div>
                        <button
                            onClick={onBatchResolve}
                            disabled={resolving || !batchField}
                            className="inline-flex h-9 items-center gap-2 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                        >
                            {resolving ? (
                                <>
                                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                    Resolving...
                                </>
                            ) : "Resolve All"}
                        </button>
                    </div>
                    {resolveResult && (
                        <p className={`mt-3 text-sm ${resolveResult.startsWith("Error") ? "text-red-600" : "text-green-600 dark:text-green-400"}`}>
                            {resolveResult}
                        </p>
                    )}
                </div>
            )}

            <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 px-5 py-3 dark:border-gray-800">
                    <div className="flex items-center gap-3">
                        <select
                            value={statusFilter}
                            onChange={e => onStatusFilterChange(e.target.value)}
                            className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                        >
                            <option value="pending">Pending</option>
                            <option value="confirmed">Confirmed</option>
                            <option value="rejected">Rejected</option>
                        </select>
                        {queueMode === "generic" ? (
                            <select
                                value={fieldFilter}
                                onChange={e => onFieldFilterChange(e.target.value)}
                                className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                            >
                                <option value="">All fields</option>
                                {summary?.by_field.map(f => (
                                    <option key={f.field_name} value={f.field_name}>{f.field_name}</option>
                                ))}
                            </select>
                        ) : (
                            <>
                                <select
                                    value={authorRouteFilter}
                                    onChange={e => onAuthorRouteFilterChange(e.target.value)}
                                    className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                                >
                                    <option value="">All routes</option>
                                    <option value="fast_path">fast_path</option>
                                    <option value="hybrid_path">hybrid_path</option>
                                    <option value="llm_path">llm_path</option>
                                    <option value="manual_review">manual_review</option>
                                </select>
                                <select
                                    value={authorReviewFilter}
                                    onChange={e => onAuthorReviewFilterChange(e.target.value)}
                                    className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                                >
                                    <option value="required">Needs review</option>
                                    <option value="all">All review states</option>
                                    <option value="not_required">No review needed</option>
                                </select>
                                <label className="inline-flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                                    <input
                                        type="checkbox"
                                        checked={authorNilOnly}
                                        onChange={e => onAuthorNilOnlyChange(e.target.checked)}
                                        className="rounded border-gray-300"
                                    />
                                    NIL only
                                </label>
                            </>
                        )}
                    </div>
                    {statusFilter === "pending" && (
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => onBulkAction("bulk-confirm")}
                                disabled={acting || selectedCount === 0}
                                className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-green-600 px-3 text-xs font-medium text-white transition-colors hover:bg-green-700 disabled:opacity-50"
                            >
                                Confirm ({selectedCount})
                            </button>
                            <button
                                onClick={() => onBulkAction("bulk-reject")}
                                disabled={acting || selectedCount === 0}
                                className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-red-600 px-3 text-xs font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-50"
                            >
                                Reject ({selectedCount})
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}
