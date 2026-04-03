"use client";

import type { AuthorityRecord, AuthorCompareResponse } from "./reviewQueueTypes";
import { SOURCE_COLORS } from "./reviewQueueTypes";

export interface AuthorReviewExpandedPanelProps {
    record: AuthorityRecord;
    compare: AuthorCompareResponse | null;
    loadingCompare: boolean;
}

export default function AuthorReviewExpandedPanel({
    record,
    compare,
    loadingCompare,
}: AuthorReviewExpandedPanelProps) {
    return (
        <div className="space-y-4">
            {loadingCompare ? (
                <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900/60 dark:text-gray-400">
                    Loading candidate comparison...
                </div>
            ) : compare?.peer_count ? (
                <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <div className="mb-3 flex items-center justify-between gap-3">
                        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                            Winner vs Runner-Up
                        </p>
                        <span className="text-xs text-gray-400 dark:text-gray-500">
                            {compare.peer_count} alternate candidates
                        </span>
                    </div>
                    <div className="space-y-3">
                        {compare.peers.map((peer) => (
                            <div
                                key={peer.id}
                                className="flex flex-col gap-2 rounded-lg border border-gray-200 p-3 dark:border-gray-700 sm:flex-row sm:items-center sm:justify-between"
                            >
                                <div className="space-y-1">
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-gray-900 dark:text-white">{peer.canonical_label}</span>
                                        <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${SOURCE_COLORS[peer.authority_source] || "bg-gray-100 text-gray-600"}`}>
                                            {peer.authority_source}
                                        </span>
                                    </div>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        {peer.authority_id} · {peer.resolution_status}
                                    </p>
                                </div>
                                <div className="grid grid-cols-3 gap-4 text-xs text-gray-500 dark:text-gray-400">
                                    <div>
                                        <p className="uppercase tracking-wide">Confidence</p>
                                        <p className="mt-1 font-mono text-gray-900 dark:text-white">{(peer.confidence * 100).toFixed(0)}%</p>
                                    </div>
                                    <div>
                                        <p className="uppercase tracking-wide">Delta</p>
                                        <p className="mt-1 font-mono text-gray-900 dark:text-white">
                                            {((record.confidence - peer.confidence) * 100).toFixed(0)} pts
                                        </p>
                                    </div>
                                    <div>
                                        <p className="uppercase tracking-wide">Route</p>
                                        <p className="mt-1 font-mono text-gray-900 dark:text-white">{peer.resolution_route || "legacy"}</p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ) : null}

            <div className="grid gap-4 lg:grid-cols-3">
                <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                        Resolution Decision
                    </p>
                    <dl className="mt-3 space-y-2 text-sm">
                        <div className="flex items-center justify-between gap-3">
                            <dt className="text-gray-500 dark:text-gray-400">Route</dt>
                            <dd className="font-mono text-gray-900 dark:text-white">{record.resolution_route || "legacy"}</dd>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <dt className="text-gray-500 dark:text-gray-400">Complexity</dt>
                            <dd className="text-gray-900 dark:text-white">
                                {typeof record.complexity_score === "number" ? record.complexity_score.toFixed(2) : "--"}
                            </dd>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <dt className="text-gray-500 dark:text-gray-400">NIL score</dt>
                            <dd className="text-rose-600 dark:text-rose-400">
                                {typeof record.nil_score === "number" ? `${(record.nil_score * 100).toFixed(0)}%` : "--"}
                            </dd>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <dt className="text-gray-500 dark:text-gray-400">Authority ID</dt>
                            <dd className="font-mono text-gray-900 dark:text-white">{record.authority_id}</dd>
                        </div>
                        <div className="flex items-center justify-between gap-3">
                            <dt className="text-gray-500 dark:text-gray-400">Resolution</dt>
                            <dd className="text-gray-900 dark:text-white">{record.resolution_status}</dd>
                        </div>
                        {record.nil_reason && (
                            <div className="flex items-center justify-between gap-3">
                                <dt className="text-gray-500 dark:text-gray-400">NIL reason</dt>
                                <dd className="font-mono text-rose-600 dark:text-rose-400">{record.nil_reason}</dd>
                            </div>
                        )}
                        {record.reformulation_trace?.attempted && (
                            <>
                                <div className="flex items-center justify-between gap-3">
                                    <dt className="text-gray-500 dark:text-gray-400">Reformulation</dt>
                                    <dd className="text-blue-600 dark:text-blue-400">
                                        {record.reformulation_trace.applied ? "applied" : "attempted"}
                                    </dd>
                                </div>
                                <div className="flex items-center justify-between gap-3">
                                    <dt className="text-gray-500 dark:text-gray-400">Retrieval gain</dt>
                                    <dd className="text-gray-900 dark:text-white">{record.reformulation_gain ?? 0}</dd>
                                </div>
                            </>
                        )}
                    </dl>
                </div>

                <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                        Score Breakdown
                    </p>
                    <div className="mt-3 space-y-2">
                        {record.score_breakdown && Object.keys(record.score_breakdown).length > 0 ? (
                            Object.entries(record.score_breakdown).map(([key, value]) => (
                                <div key={key} className="flex items-center justify-between gap-3 text-sm">
                                    <span className="text-gray-500 dark:text-gray-400">{key.replaceAll("_", " ")}</span>
                                    <span className="font-mono text-gray-900 dark:text-white">
                                        {typeof value === "number" ? value.toFixed(2) : String(value)}
                                    </span>
                                </div>
                            ))
                        ) : (
                            <p className="text-sm text-gray-400 dark:text-gray-500">No structured score breakdown.</p>
                        )}
                    </div>
                </div>

                <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                    <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Evidence</p>
                    <div className="mt-3 flex flex-wrap gap-2">
                        {record.evidence && record.evidence.length > 0 ? (
                            record.evidence.map((item) => (
                                <span
                                    key={item}
                                    className="inline-flex rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300"
                                >
                                    {item}
                                </span>
                            ))
                        ) : (
                            <p className="text-sm text-gray-400 dark:text-gray-500">No evidence captured.</p>
                        )}
                    </div>
                    <div className="mt-4 space-y-3">
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Merged Sources</p>
                            <div className="mt-2 flex flex-wrap gap-2">
                                {record.merged_sources && record.merged_sources.length > 0 ? (
                                    record.merged_sources.map((source) => (
                                        <span
                                            key={source}
                                            className="inline-flex rounded-full bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300"
                                        >
                                            {source}
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-xs text-gray-400 dark:text-gray-500">None</span>
                                )}
                            </div>
                        </div>
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Aliases</p>
                            <div className="mt-2 flex flex-wrap gap-2">
                                {record.aliases && record.aliases.length > 0 ? (
                                    record.aliases.map((alias) => (
                                        <span
                                            key={alias}
                                            className="inline-flex rounded-full bg-emerald-50 px-2 py-1 text-xs text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-300"
                                        >
                                            {alias}
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-xs text-gray-400 dark:text-gray-500">None</span>
                                )}
                            </div>
                        </div>
                        {record.reformulation_trace?.attempted && (
                            <div>
                                <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                    Reformulation Trace
                                </p>
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {record.reformulation_trace.generated_queries && record.reformulation_trace.generated_queries.length > 0 ? (
                                        record.reformulation_trace.generated_queries.map((query) => (
                                            <span
                                                key={query}
                                                className="inline-flex rounded-full bg-sky-50 px-2 py-1 text-xs text-sky-700 dark:bg-sky-500/10 dark:text-sky-300"
                                            >
                                                {query}
                                            </span>
                                        ))
                                    ) : (
                                        <span className="text-xs text-gray-400 dark:text-gray-500">No alternate queries kept</span>
                                    )}
                                </div>
                                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                                    {record.reformulation_trace.provider || "provider-unavailable"}
                                    {record.reformulation_trace.model ? ` · ${record.reformulation_trace.model}` : ""}
                                    {typeof record.reformulation_cost_estimate === "number" ? ` · est. $${record.reformulation_cost_estimate.toFixed(4)}` : ""}
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
