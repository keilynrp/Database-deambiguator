"use client";

import { useCallback, useEffect, useState } from "react";
import { useToast } from "../components/ui";
import { apiFetch } from "@/lib/api";
import type { DomainAttribute, DomainSchema } from "../contexts/DomainContext";
import ReviewQueueRecordsTable from "./ReviewQueueRecordsTable";
import ReviewQueueSummaryPanels from "./ReviewQueueSummaryPanels";
import {
    type AuthorCompareResponse,
    type AuthorMetrics,
    type AuthorQueueResponse,
    type AuthorQueueSummary,
    type AuthorityRecord,
    type QueueSummary,
} from "./reviewQueueTypes";

export default function ReviewQueueTab({ activeDomain }: { activeDomain: DomainSchema | null }) {
    const { toast } = useToast();
    const [summary, setSummary] = useState<QueueSummary | null>(null);
    const [authorSummary, setAuthorSummary] = useState<AuthorQueueSummary | null>(null);
    const [authorMetrics, setAuthorMetrics] = useState<AuthorMetrics | null>(null);
    const [records, setRecords] = useState<AuthorityRecord[]>([]);
    const [loadingRecords, setLoadingRecords] = useState(false);
    const [selected, setSelected] = useState<Set<number>>(new Set());
    const [acting, setActing] = useState(false);
    const [rowActionId, setRowActionId] = useState<number | null>(null);
    const [queueMode, setQueueMode] = useState<"generic" | "authors">("generic");
    const [statusFilter, setStatusFilter] = useState("pending");
    const [fieldFilter, setFieldFilter] = useState("");
    const [authorRouteFilter, setAuthorRouteFilter] = useState("");
    const [authorReviewFilter, setAuthorReviewFilter] = useState("required");
    const [authorNilOnly, setAuthorNilOnly] = useState(false);
    const [batchField, setBatchField] = useState("");
    const [batchEntityType, setBatchEntityType] = useState("general");
    const [batchLimit, setBatchLimit] = useState(20);
    const [resolving, setResolving] = useState(false);
    const [resolveResult, setResolveResult] = useState<string | null>(null);
    const [expandedId, setExpandedId] = useState<number | null>(null);
    const [compareMap, setCompareMap] = useState<Record<number, AuthorCompareResponse>>({});
    const [loadingCompareId, setLoadingCompareId] = useState<number | null>(null);

    // Auto-select first string field for batch resolve
    useEffect(() => {
        if (activeDomain && !batchField) {
            const firstStr = activeDomain.attributes.find((a: DomainAttribute) => a.type === "string");
            if (firstStr) setBatchField(firstStr.name);
        }
    }, [activeDomain, batchField]);

    const fetchSummary = useCallback(async () => {
        try {
            if (queueMode === "authors") {
                const [queueRes, metricsRes] = await Promise.all([
                    apiFetch("/authority/authors/review-queue"),
                    apiFetch("/authority/authors/metrics"),
                ]);
                if (queueRes.ok) {
                    const payload: AuthorQueueResponse = await queueRes.json();
                    setAuthorSummary(payload.summary);
                    setSummary(null);
                }
                if (metricsRes.ok) {
                    setAuthorMetrics(await metricsRes.json());
                }
            } else {
                const res = await apiFetch("/authority/queue/summary");
                if (res.ok) {
                    setSummary(await res.json());
                    setAuthorSummary(null);
                    setAuthorMetrics(null);
                }
            }
        } catch {}
    }, [queueMode]);

    const fetchRecords = useCallback(async () => {
        setLoadingRecords(true);
        try {
            if (queueMode === "authors") {
                const params = new URLSearchParams({ status: statusFilter, limit: "100" });
                if (authorRouteFilter) params.set("route", authorRouteFilter);
                if (authorReviewFilter === "required") params.set("review_required", "true");
                if (authorReviewFilter === "not_required") params.set("review_required", "false");
                if (authorNilOnly) params.set("nil_only", "true");

                const res = await apiFetch(`/authority/authors/review-queue?${params.toString()}`);
                if (res.ok) {
                    const data: AuthorQueueResponse = await res.json();
                    setRecords(data.records ?? []);
                    setAuthorSummary(data.summary);
                    setSelected(new Set());
                }
            } else {
                const params = new URLSearchParams({ status: statusFilter, limit: "100" });
                if (fieldFilter) params.set("field_name", fieldFilter);
                const res = await apiFetch(`/authority/records?${params.toString()}`);
                if (res.ok) {
                    const data = await res.json();
                    setRecords(data.records ?? []);
                    setSelected(new Set());
                }
            }
        } catch {
        } finally {
            setLoadingRecords(false);
        }
    }, [statusFilter, fieldFilter, queueMode, authorRouteFilter, authorReviewFilter, authorNilOnly]);

    useEffect(() => { fetchSummary(); }, [fetchSummary]);
    useEffect(() => { fetchRecords(); }, [fetchRecords]);

    function toggleSelect(id: number) {
        setSelected(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id); else next.add(id);
            return next;
        });
    }

    function toggleSelectAll() {
        if (selected.size === records.length) {
            setSelected(new Set());
        } else {
            setSelected(new Set(records.map(r => r.id)));
        }
    }

    async function bulkAction(action: "bulk-confirm" | "bulk-reject") {
        if (selected.size === 0) return;
        setActing(true);
        try {
            const res = await apiFetch(`/authority/records/${action}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ids: Array.from(selected), also_create_rules: true }),
            });
            if (res.ok) {
                await fetchSummary();
                await fetchRecords();
            }
        } catch {
        } finally {
            setActing(false);
        }
    }

    async function batchResolve() {
        if (!batchField) return;
        setResolving(true);
        setResolveResult(null);
        try {
            const res = await apiFetch("/authority/resolve/batch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    field_name: batchField,
                    entity_type: batchEntityType,
                    limit: batchLimit,
                }),
            });
            if (res.ok) {
                const data = await res.json();
                setResolveResult(
                    `Resolved ${data.resolved_count} values, created ${data.records_created} records` +
                    (data.already_existed_count ? `, ${data.already_existed_count} already existed` : "")
                );
                await fetchSummary();
                await fetchRecords();
            } else {
                const err = await res.json().catch(() => ({}));
                setResolveResult(`Error: ${err.detail || res.statusText}`);
            }
        } catch {
            setResolveResult("Network error");
        } finally {
            setResolving(false);
        }
    }

    async function reviewRecord(rec: AuthorityRecord, action: "confirm" | "reject") {
        setRowActionId(rec.id);
        try {
            const res = await apiFetch(`/authority/records/${rec.id}/${action}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: action === "confirm"
                    ? JSON.stringify({ also_create_rule: !rec.nil_reason })
                    : undefined,
            });
            if (!res.ok) {
                toast(`Failed to ${action} record`, "error");
                return;
            }
            toast(
                action === "confirm"
                    ? (rec.nil_reason ? "NIL case accepted" : "Author candidate confirmed")
                    : "Author candidate rejected",
                "success"
            );
            await fetchSummary();
            await fetchRecords();
        } catch {
            toast(`Failed to ${action} record`, "error");
        } finally {
            setRowActionId(null);
        }
    }

    async function toggleExpanded(rec: AuthorityRecord) {
        const nextExpanded = expandedId === rec.id ? null : rec.id;
        setExpandedId(nextExpanded);
        if (queueMode !== "authors" || nextExpanded === null || compareMap[rec.id]) {
            return;
        }

        setLoadingCompareId(rec.id);
        try {
            const res = await apiFetch(`/authority/authors/review-queue/${rec.id}/compare`);
            if (res.ok) {
                const payload: AuthorCompareResponse = await res.json();
                setCompareMap(prev => ({ ...prev, [rec.id]: payload }));
            }
        } catch {
        } finally {
            setLoadingCompareId(current => (current === rec.id ? null : current));
        }
    }

    return (
        <div className="space-y-6">
            <div className="inline-flex rounded-xl border border-gray-200 bg-white p-1 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <button
                    onClick={() => setQueueMode("generic")}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                        queueMode === "generic"
                            ? "bg-blue-600 text-white"
                            : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    }`}
                >
                    Generic Queue
                </button>
                <button
                    onClick={() => setQueueMode("authors")}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                        queueMode === "authors"
                            ? "bg-blue-600 text-white"
                            : "text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
                    }`}
                >
                    Author Queue
                </button>
            </div>

            <ReviewQueueSummaryPanels
                queueMode={queueMode}
                summary={summary}
                authorSummary={authorSummary}
                authorMetrics={authorMetrics}
            />

            {/* Batch resolve panel */}
            {queueMode === "generic" && (
            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-3 text-sm font-medium text-gray-900 dark:text-white">Batch Resolve</h3>
                <div className="flex flex-wrap items-end gap-4">
                    <div className="min-w-[160px]">
                        <label className="mb-1 block text-xs text-gray-500 dark:text-gray-400">Field</label>
                        <select
                            value={batchField}
                            onChange={e => setBatchField(e.target.value)}
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
                            onChange={e => setBatchEntityType(e.target.value)}
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
                            onChange={e => setBatchLimit(Number(e.target.value))}
                            className="h-9 w-full rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                        />
                    </div>
                    <button
                        onClick={batchResolve}
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

            {/* Records filter + bulk actions */}
            <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 px-5 py-3 dark:border-gray-800">
                    <div className="flex items-center gap-3">
                        <select
                            value={statusFilter}
                            onChange={e => setStatusFilter(e.target.value)}
                            className="h-8 rounded-lg border border-gray-200 bg-white px-2 text-sm dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                        >
                            <option value="pending">Pending</option>
                            <option value="confirmed">Confirmed</option>
                            <option value="rejected">Rejected</option>
                        </select>
                        {queueMode === "generic" ? (
                            <select
                                value={fieldFilter}
                                onChange={e => setFieldFilter(e.target.value)}
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
                                    onChange={e => setAuthorRouteFilter(e.target.value)}
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
                                    onChange={e => setAuthorReviewFilter(e.target.value)}
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
                                        onChange={e => setAuthorNilOnly(e.target.checked)}
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
                                onClick={() => bulkAction("bulk-confirm")}
                                disabled={acting || selected.size === 0}
                                className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-green-600 px-3 text-xs font-medium text-white transition-colors hover:bg-green-700 disabled:opacity-50"
                            >
                                Confirm ({selected.size})
                            </button>
                            <button
                                onClick={() => bulkAction("bulk-reject")}
                                disabled={acting || selected.size === 0}
                                className="inline-flex h-8 items-center gap-1.5 rounded-lg bg-red-600 px-3 text-xs font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-50"
                            >
                                Reject ({selected.size})
                            </button>
                        </div>
                    )}
                </div>

                <ReviewQueueRecordsTable
                    queueMode={queueMode}
                    statusFilter={statusFilter}
                    loadingRecords={loadingRecords}
                    records={records}
                    selected={selected}
                    rowActionId={rowActionId}
                    expandedId={expandedId}
                    loadingCompareId={loadingCompareId}
                    compareMap={compareMap}
                    onToggleSelectAll={toggleSelectAll}
                    onToggleSelect={toggleSelect}
                    onReviewRecord={reviewRecord}
                    onToggleExpanded={toggleExpanded}
                />
            </div>
        </div>
    );
}

