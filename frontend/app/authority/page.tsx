"use client";

import { useState, useEffect, useCallback, Fragment } from "react";
import { PageHeader, TabNav, Badge, useToast } from "../components/ui";
import { useDomain, type DomainAttribute, type DomainSchema } from "../contexts/DomainContext";
import { useLanguage } from "../contexts/LanguageContext";
import { apiFetch } from "@/lib/api";
import AnnotationThread from "../components/AnnotationThread";

// ── Shared types ────────────────────────────────────────────────────────────

interface AuthorityGroup {
    main: string;
    variations: string[];
    count: number;
    has_rules: boolean;
    resolved_to: string | null;
}

interface AuthorityResponse {
    groups: AuthorityGroup[];
    total_groups: number;
    total_rules: number;
    pending_groups: number;
}

interface ApplyResult {
    rules_applied: number;
    records_updated: number;
}

interface GroupState {
    canonical: string;
    excluded: Set<string>;
    saved: boolean;
}

// ── Review Queue types ──────────────────────────────────────────────────────

interface QueueSummary {
    total_pending: number;
    total_confirmed: number;
    total_rejected: number;
    by_field: {
        field_name: string;
        pending: number;
        confirmed: number;
        rejected: number;
        avg_confidence: number;
    }[];
}

interface AuthorityRecord {
    id: number;
    field_name: string;
    original_value: string;
    authority_source: string;
    authority_id: string;
    canonical_label: string;
    aliases: string[];
    description: string | null;
    confidence: number;
    uri: string | null;
    status: string;
    created_at: string;
    confirmed_at: string | null;
    resolution_status: string;
    score_breakdown?: Record<string, number> | null;
    evidence?: string[] | null;
    merged_sources?: string[] | null;
    resolution_route?: string | null;
    complexity_score?: number | null;
    review_required?: boolean;
    nil_reason?: string | null;
    nil_score?: number | null;
}

interface AuthorQueueSummary {
    total_records: number;
    pending_review: number;
    nil_cases: number;
    by_nil_reason?: Record<string, number>;
    by_route: Record<string, number>;
    by_status: Record<string, number>;
}

interface AuthorQueueResponse {
    total: number;
    records: AuthorityRecord[];
    summary: AuthorQueueSummary;
}

interface AuthorMetrics {
    total_records: number;
    pending_review: number;
    nil_cases: number;
    avg_confidence: number;
    avg_complexity: number;
    avg_nil_score: number;
    review_rate: number;
    nil_rate: number;
    confirm_rate: number;
    reject_rate: number;
    by_nil_reason: Record<string, number>;
    by_route: Record<string, number>;
    by_status: Record<string, number>;
}

interface AuthorCompareResponse {
    subject: AuthorityRecord;
    peers: AuthorityRecord[];
    peer_count: number;
}

// ── Source badge colors ─────────────────────────────────────────────────────

const SOURCE_COLORS: Record<string, string> = {
    wikidata: "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
    viaf: "bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
    orcid: "bg-green-100 text-green-700 dark:bg-green-500/10 dark:text-green-400",
    dbpedia: "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400",
    openalex: "bg-violet-100 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
};

// ═════════════════════════════════════════════════════════════════════════════
// Review Queue Tab
// ═════════════════════════════════════════════════════════════════════════════

function ReviewQueueTab({ activeDomain }: { activeDomain: DomainSchema | null }) {
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

            {/* Summary cards */}
            {queueMode === "generic" && summary && (
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
            )}

            {queueMode === "authors" && authorSummary && (
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
            )}

            {queueMode === "authors" && authorMetrics && (
                <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <h3 className="text-sm font-medium text-gray-900 dark:text-white">Engine Metrics</h3>
                        <span className="text-xs text-gray-400 dark:text-gray-500">author-only runtime</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
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
                    </div>
                </div>
            )}

            {queueMode === "authors" && authorMetrics && Object.keys(authorMetrics.by_nil_reason).length > 0 && (
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

            {/* Per-field breakdown */}
            {queueMode === "generic" && summary && summary.by_field.length > 0 && (
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

            {queueMode === "authors" && authorSummary && Object.keys(authorSummary.by_route).length > 0 && (
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

                {/* Records table */}
                {loadingRecords ? (
                    <div className="flex items-center justify-center py-12">
                        <svg className="h-6 w-6 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                    </div>
                ) : records.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12">
                        <p className="text-sm text-gray-400 dark:text-gray-500">
                            No {statusFilter} records found
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-100 text-left text-xs font-medium text-gray-500 dark:border-gray-800 dark:text-gray-400">
                                    {statusFilter === "pending" && (
                                        <th className="px-4 py-2 w-10">
                                            <input
                                                type="checkbox"
                                                checked={selected.size === records.length && records.length > 0}
                                                onChange={toggleSelectAll}
                                                className="rounded border-gray-300"
                                            />
                                        </th>
                                    )}
                                    <th className="px-4 py-2">Original Value</th>
                                    <th className="px-4 py-2">{queueMode === "authors" ? "Candidate" : "Canonical Label"}</th>
                                    <th className="px-4 py-2">Source</th>
                                    <th className="px-4 py-2">Confidence</th>
                                    <th className="px-4 py-2">{queueMode === "authors" ? "Route" : "Field"}</th>
                                    <th className="px-4 py-2">Status</th>
                                    <th className="px-4 py-2">{queueMode === "authors" ? "Actions" : ""}</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50 dark:divide-gray-800">
                                {records.map(rec => (
                                    <Fragment key={rec.id}>
                                    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                                        {statusFilter === "pending" && (
                                            <td className="px-4 py-2.5">
                                                <input
                                                    type="checkbox"
                                                    checked={selected.has(rec.id)}
                                                    onChange={() => toggleSelect(rec.id)}
                                                    className="rounded border-gray-300"
                                                />
                                            </td>
                                        )}
                                        <td className="px-4 py-2.5 font-medium text-gray-900 dark:text-white">
                                            {rec.original_value}
                                        </td>
                                        <td className="px-4 py-2.5 text-gray-700 dark:text-gray-300">
                                            <div className="flex items-center gap-2">
                                                {rec.canonical_label}
                                                {queueMode === "authors" && rec.nil_reason && (
                                                    <Badge variant="error">NIL</Badge>
                                                )}
                                                {rec.uri && (
                                                    <a
                                                        href={rec.uri}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-blue-500 hover:text-blue-600"
                                                        title="View in authority source"
                                                    >
                                                        <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                        </svg>
                                                    </a>
                                                )}
                                            </div>
                                            {rec.description && (
                                                <p className="mt-0.5 text-xs text-gray-400 dark:text-gray-500 truncate max-w-xs">
                                                    {rec.description}
                                                </p>
                                            )}
                                            {queueMode === "authors" && rec.nil_reason && (
                                                <p className="mt-0.5 text-xs text-rose-500 dark:text-rose-400">
                                                    {rec.nil_reason}
                                                </p>
                                            )}
                                        </td>
                                        <td className="px-4 py-2.5">
                                            <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${SOURCE_COLORS[rec.authority_source] || "bg-gray-100 text-gray-600"}`}>
                                                {rec.authority_source}
                                            </span>
                                        </td>
                                        <td className="px-4 py-2.5">
                                            <div className="flex items-center gap-2">
                                                <div className="h-1.5 w-16 overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
                                                    <div
                                                        className={`h-full rounded-full ${rec.confidence >= 0.8 ? "bg-green-500" : rec.confidence >= 0.5 ? "bg-amber-500" : "bg-red-500"}`}
                                                        style={{ width: `${rec.confidence * 100}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-gray-500">{(rec.confidence * 100).toFixed(0)}%</span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-2.5 font-mono text-xs text-gray-500">
                                            {queueMode === "authors" ? (
                                                <div className="space-y-1">
                                                    <div>{rec.resolution_route || "legacy"}</div>
                                                    <div className="text-[11px] text-gray-400">
                                                        complexity {typeof rec.complexity_score === "number" ? rec.complexity_score.toFixed(2) : "--"}
                                                    </div>
                                                    <div className="text-[11px] text-rose-500 dark:text-rose-400">
                                                        nil {typeof rec.nil_score === "number" ? `${(rec.nil_score * 100).toFixed(0)}%` : "--"}
                                                    </div>
                                                </div>
                                            ) : rec.field_name}
                                        </td>
                                        <td className="px-4 py-2.5">
                                            <div className="flex flex-col items-start gap-1">
                                                <Badge variant={rec.status === "confirmed" ? "success" : rec.status === "rejected" ? "error" : "warning"}>
                                                    {rec.status}
                                                </Badge>
                                                {queueMode === "authors" && rec.review_required && (
                                                    <span className="text-[11px] text-amber-600 dark:text-amber-400">needs review</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-4 py-2.5">
                                            <div className="flex items-center justify-end gap-2">
                                                {queueMode === "authors" && statusFilter === "pending" && (
                                                    <>
                                                        <button
                                                            onClick={() => reviewRecord(rec, "confirm")}
                                                            disabled={rowActionId === rec.id}
                                                            className="inline-flex h-7 items-center rounded-md bg-green-600 px-2.5 text-[11px] font-medium text-white transition-colors hover:bg-green-700 disabled:opacity-50"
                                                        >
                                                            {rowActionId === rec.id ? "Saving..." : rec.nil_reason ? "Accept NIL" : "Confirm"}
                                                        </button>
                                                        <button
                                                            onClick={() => reviewRecord(rec, "reject")}
                                                            disabled={rowActionId === rec.id}
                                                            className="inline-flex h-7 items-center rounded-md bg-red-600 px-2.5 text-[11px] font-medium text-white transition-colors hover:bg-red-700 disabled:opacity-50"
                                                        >
                                                            Reject
                                                        </button>
                                                    </>
                                                )}
                                                <button
                                                    onClick={() => toggleExpanded(rec)}
                                                    className={`rounded p-1 transition-colors ${expandedId === rec.id ? "text-indigo-600 dark:text-indigo-400" : "text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"}`}
                                                    title="Toggle comments"
                                                >
                                                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                                                    </svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    {expandedId === rec.id && (
                                        <tr>
                                            <td colSpan={statusFilter === "pending" ? 8 : 7} className="px-6 py-4 bg-gray-50 dark:bg-gray-800/30 border-t border-gray-100 dark:border-gray-800">
                                                <div className="space-y-4">
                                                    {queueMode === "authors" && (
                                                        <div className="space-y-4">
                                                            {loadingCompareId === rec.id ? (
                                                                <div className="rounded-xl border border-gray-200 bg-white p-4 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-900/60 dark:text-gray-400">
                                                                    Loading candidate comparison...
                                                                </div>
                                                            ) : compareMap[rec.id]?.peer_count ? (
                                                                <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                                                                    <div className="mb-3 flex items-center justify-between gap-3">
                                                                        <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                                                            Winner vs Runner-Up
                                                                        </p>
                                                                        <span className="text-xs text-gray-400 dark:text-gray-500">
                                                                            {compareMap[rec.id].peer_count} alternate candidates
                                                                        </span>
                                                                    </div>
                                                                    <div className="space-y-3">
                                                                        {compareMap[rec.id].peers.map(peer => (
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
                                                                                            {((rec.confidence - peer.confidence) * 100).toFixed(0)} pts
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
                                                                        <dd className="font-mono text-gray-900 dark:text-white">{rec.resolution_route || "legacy"}</dd>
                                                                    </div>
                                                                    <div className="flex items-center justify-between gap-3">
                                                                        <dt className="text-gray-500 dark:text-gray-400">Complexity</dt>
                                                                        <dd className="text-gray-900 dark:text-white">
                                                                            {typeof rec.complexity_score === "number" ? rec.complexity_score.toFixed(2) : "--"}
                                                                        </dd>
                                                                    </div>
                                                                    <div className="flex items-center justify-between gap-3">
                                                                        <dt className="text-gray-500 dark:text-gray-400">NIL score</dt>
                                                                        <dd className="text-rose-600 dark:text-rose-400">
                                                                            {typeof rec.nil_score === "number" ? `${(rec.nil_score * 100).toFixed(0)}%` : "--"}
                                                                        </dd>
                                                                    </div>
                                                                    <div className="flex items-center justify-between gap-3">
                                                                        <dt className="text-gray-500 dark:text-gray-400">Authority ID</dt>
                                                                        <dd className="font-mono text-gray-900 dark:text-white">{rec.authority_id}</dd>
                                                                    </div>
                                                                    <div className="flex items-center justify-between gap-3">
                                                                        <dt className="text-gray-500 dark:text-gray-400">Resolution</dt>
                                                                        <dd className="text-gray-900 dark:text-white">{rec.resolution_status}</dd>
                                                                    </div>
                                                                    {rec.nil_reason && (
                                                                        <div className="flex items-center justify-between gap-3">
                                                                            <dt className="text-gray-500 dark:text-gray-400">NIL reason</dt>
                                                                            <dd className="font-mono text-rose-600 dark:text-rose-400">{rec.nil_reason}</dd>
                                                                        </div>
                                                                    )}
                                                                </dl>
                                                            </div>

                                                            <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/60">
                                                                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                                                    Score Breakdown
                                                                </p>
                                                                <div className="mt-3 space-y-2">
                                                                    {rec.score_breakdown && Object.keys(rec.score_breakdown).length > 0 ? (
                                                                        Object.entries(rec.score_breakdown).map(([key, value]) => (
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
                                                                <p className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                                                    Evidence
                                                                </p>
                                                                <div className="mt-3 flex flex-wrap gap-2">
                                                                    {rec.evidence && rec.evidence.length > 0 ? (
                                                                        rec.evidence.map(item => (
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
                                                                        <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                                                            Merged Sources
                                                                        </p>
                                                                        <div className="mt-2 flex flex-wrap gap-2">
                                                                            {rec.merged_sources && rec.merged_sources.length > 0 ? (
                                                                                rec.merged_sources.map(source => (
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
                                                                        <p className="text-[11px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                                                            Aliases
                                                                        </p>
                                                                        <div className="mt-2 flex flex-wrap gap-2">
                                                                            {rec.aliases && rec.aliases.length > 0 ? (
                                                                                rec.aliases.map(alias => (
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
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    )}

                                                    <AnnotationThread authorityId={rec.id} />
                                                </div>
                                            </td>
                                        </tr>
                                    )}
                                    </Fragment>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}

// ═════════════════════════════════════════════════════════════════════════════
// Disambiguation Tab (existing)
// ═════════════════════════════════════════════════════════════════════════════

function DisambiguationTab({ activeDomain }: { activeDomain: DomainSchema | null }) {
    const { toast } = useToast();
    const [field, setField] = useState("");

    useEffect(() => {
        if (activeDomain && !field) {
            const firstStr = activeDomain.attributes.find((a: DomainAttribute) => a.type === "string");
            if (firstStr) setField(firstStr.name);
        }
    }, [activeDomain, field]);

    const [data, setData] = useState<AuthorityResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [applying, setApplying] = useState(false);
    const [applyResult, setApplyResult] = useState<ApplyResult | null>(null);
    const [groupStates, setGroupStates] = useState<Record<number, GroupState>>({});
    const [savingGroup, setSavingGroup] = useState<number | null>(null);
    const [page, setPage] = useState(0);
    const [limit, setLimit] = useState(20);

    useEffect(() => { setPage(0); }, [data]);

    const visibleGroups = data ? data.groups.slice(page * limit, (page + 1) * limit) : [];

    async function analyze() {
        setLoading(true);
        setData(null);
        setGroupStates({});
        setApplyResult(null);
        try {
            const res = await apiFetch(`/authority/${field}`);
            if (!res.ok) throw new Error("Failed to fetch");
            const json: AuthorityResponse = await res.json();
            setData(json);
            const states: Record<number, GroupState> = {};
            json.groups.forEach((g, idx) => {
                states[idx] = { canonical: g.resolved_to || g.main, excluded: new Set<string>(), saved: g.has_rules };
            });
            setGroupStates(states);
        } catch {
            toast("Error fetching authority data", "error");
        } finally {
            setLoading(false);
        }
    }

    function updateCanonical(idx: number, value: string) {
        setGroupStates(prev => ({ ...prev, [idx]: { ...prev[idx], canonical: value, saved: false } }));
    }

    function toggleExclude(idx: number, variation: string) {
        setGroupStates(prev => {
            const excluded = new Set(prev[idx].excluded);
            if (excluded.has(variation)) excluded.delete(variation); else excluded.add(variation);
            return { ...prev, [idx]: { ...prev[idx], excluded, saved: false } };
        });
    }

    async function saveGroupRules(idx: number) {
        if (!data) return;
        const group = data.groups[idx];
        const state = groupStates[idx];
        const activeVariations = group.variations.filter(v => !state.excluded.has(v));
        setSavingGroup(idx);
        try {
            const res = await apiFetch("/rules/bulk", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ field_name: field, canonical_value: state.canonical, variations: activeVariations }),
            });
            if (!res.ok) throw new Error("Failed to save rules");
            setGroupStates(prev => ({ ...prev, [idx]: { ...prev[idx], saved: true } }));
        } catch {
            toast("Error saving rules", "error");
        } finally {
            setSavingGroup(null);
        }
    }

    async function applyAllRules() {
        setApplying(true);
        setApplyResult(null);
        try {
            const res = await apiFetch(`/rules/apply?field_name=${field}`, { method: "POST" });
            if (!res.ok) throw new Error("Failed to apply rules");
            setApplyResult(await res.json());
        } catch {
            toast("Error applying rules", "error");
        } finally {
            setApplying(false);
        }
    }

    const savedCount = Object.values(groupStates).filter(s => s.saved).length;

    return (
        <div className="space-y-6">
            {/* Controls */}
            <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex flex-wrap items-end gap-4">
                    <div className="min-w-[200px] flex-1">
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Field to Normalize
                        </label>
                        <select
                            value={field}
                            onChange={e => setField(e.target.value)}
                            className="h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200"
                        >
                            {activeDomain ? (
                                activeDomain.attributes
                                    .filter((a: DomainAttribute) => a.type === "string")
                                    .map((attr: DomainAttribute) => (
                                        <option key={attr.name} value={attr.name}>{attr.label}</option>
                                    ))
                            ) : (
                                <option value="">Loading attributes...</option>
                            )}
                        </select>
                    </div>
                    <button
                        onClick={analyze}
                        disabled={loading}
                        className="inline-flex h-10 items-center gap-2 rounded-lg bg-blue-600 px-5 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                        {loading ? (
                            <>
                                <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                </svg>
                                Analyzing...
                            </>
                        ) : (
                            <>
                                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                                Analyze
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Stats summary */}
            {data && (
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Variation Groups</p>
                        <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{data.total_groups}</p>
                    </div>
                    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Existing Rules</p>
                        <p className="mt-1 text-2xl font-bold text-gray-900 dark:text-white">{data.total_rules}</p>
                    </div>
                    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                        <p className="text-sm text-gray-500 dark:text-gray-400">Pending Review</p>
                        <p className="mt-1 text-2xl font-bold text-amber-600 dark:text-amber-400">{data.pending_groups}</p>
                    </div>
                </div>
            )}

            {/* Groups list */}
            {data && (
                <div className="space-y-4">
                    {visibleGroups.map((group, idx) => {
                        const originalIdx = page * limit + idx;
                        const state = groupStates[originalIdx];
                        if (!state) return null;
                        return (
                            <div key={originalIdx} className={`rounded-2xl border bg-white p-5 transition-shadow hover:shadow-md dark:bg-gray-900 ${state.saved ? "border-green-200 dark:border-green-800" : "border-gray-200 dark:border-gray-800"}`}>
                                <div className="mb-4 flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <Badge variant={state.saved ? "success" : "warning"} dot>
                                            {state.saved ? "Resolved" : "Pending"}
                                        </Badge>
                                        <span className="text-xs text-gray-400 dark:text-gray-500">{group.count} variations</span>
                                    </div>
                                    <button
                                        onClick={() => saveGroupRules(originalIdx)}
                                        disabled={savingGroup === originalIdx}
                                        className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        {savingGroup === originalIdx ? "Saving..." : (
                                            <>
                                                <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                </svg>
                                                Save Rules
                                            </>
                                        )}
                                    </button>
                                </div>
                                <div className="mb-3">
                                    <label className="mb-1 block text-xs font-medium text-gray-500 dark:text-gray-400">Canonical Value</label>
                                    <input
                                        type="text"
                                        value={state.canonical}
                                        onChange={e => updateCanonical(originalIdx, e.target.value)}
                                        className="h-9 w-full max-w-md rounded-lg border border-gray-200 bg-white px-3 text-sm font-semibold text-gray-900 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                                    />
                                </div>
                                <div>
                                    <label className="mb-1.5 block text-xs font-medium text-gray-500 dark:text-gray-400">Variations (click to exclude)</label>
                                    <div className="flex flex-wrap gap-2">
                                        {group.variations.map((v, i) => {
                                            const isExcluded = state.excluded.has(v);
                                            const isCanonical = v === state.canonical;
                                            return (
                                                <button
                                                    key={i}
                                                    onClick={() => { if (!isCanonical) toggleExclude(originalIdx, v); }}
                                                    className={`inline-flex items-center gap-1 rounded-lg border px-2.5 py-1 text-sm transition-colors ${isCanonical
                                                        ? "border-blue-300 bg-blue-50 text-blue-700 dark:border-blue-700 dark:bg-blue-500/10 dark:text-blue-400"
                                                        : isExcluded
                                                            ? "border-gray-200 bg-gray-50 text-gray-300 line-through dark:border-gray-800 dark:bg-gray-800/50 dark:text-gray-600"
                                                            : "border-gray-200 bg-gray-50 text-gray-700 hover:border-red-300 hover:bg-red-50 hover:text-red-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300 dark:hover:border-red-700 dark:hover:bg-red-500/10 dark:hover:text-red-400"
                                                    }`}
                                                    title={isCanonical ? "Canonical value" : isExcluded ? "Click to include" : "Click to exclude"}
                                                >
                                                    {v}
                                                    {isCanonical && <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>}
                                                </button>
                                            );
                                        })}
                                    </div>
                                </div>
                            </div>
                        );
                    })}

                    {/* Pagination */}
                    {data.groups.length > 0 && (
                        <div className="flex items-center justify-between border-t border-gray-200 pt-4 dark:border-gray-800">
                            <div className="flex items-center gap-2">
                                <span className="text-sm text-gray-500 dark:text-gray-400">Rows per page:</span>
                                <select
                                    value={limit}
                                    onChange={e => { setLimit(Number(e.target.value)); setPage(0); }}
                                    className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-sm text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                                >
                                    {[10, 20, 50, 100].map(n => <option key={n} value={n}>{n}</option>)}
                                </select>
                            </div>
                            <div className="flex items-center gap-4">
                                <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3.5 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800">
                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                                    Previous
                                </button>
                                <div className="flex items-center gap-2">
                                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-medium text-white">{page + 1}</span>
                                    <span className="text-sm text-gray-500">of {Math.ceil(data.groups.length / limit)}</span>
                                </div>
                                <button onClick={() => setPage(p => p + 1)} disabled={(page + 1) * limit >= data.groups.length} className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3.5 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800">
                                    Next
                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                                </button>
                            </div>
                        </div>
                    )}

                    {data.groups.length === 0 && (
                        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 py-16 dark:border-gray-700">
                            <svg className="mb-3 h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-sm font-medium text-gray-500 dark:text-gray-400">No variation groups found</p>
                            <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">The data for this field appears to be consistent</p>
                        </div>
                    )}
                </div>
            )}

            {/* Empty state */}
            {!data && !loading && (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-gray-300 py-16 dark:border-gray-700">
                    <svg className="mb-3 h-12 w-12 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                    <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Authority Control Dictionary</p>
                    <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">Select a field and click Analyze to find data inconsistencies</p>
                </div>
            )}

            {/* Apply rules bar */}
            {data && data.total_groups > 0 && (
                <div className="sticky bottom-0 rounded-2xl border border-gray-200 bg-white p-4 shadow-lg dark:border-gray-800 dark:bg-gray-900">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                {savedCount} of {data.total_groups} groups resolved
                            </p>
                            {applyResult && (
                                <p className="text-xs text-green-600 dark:text-green-400">
                                    Applied {applyResult.rules_applied} rules, updated {applyResult.records_updated} records
                                </p>
                            )}
                        </div>
                        <button
                            onClick={applyAllRules}
                            disabled={applying || savedCount === 0}
                            className="inline-flex h-10 items-center gap-2 rounded-lg bg-green-600 px-5 text-sm font-medium text-white transition-colors hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            {applying ? (
                                <>
                                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                    </svg>
                                    Applying...
                                </>
                            ) : (
                                <>
                                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                    </svg>
                                    Apply All Rules to Database
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}

// ═════════════════════════════════════════════════════════════════════════════
// Main Page with Tabs
// ═════════════════════════════════════════════════════════════════════════════

export default function AuthorityPage() {
    const { activeDomain } = useDomain();
    const { t } = useLanguage();
    const [tab, setTab] = useState<"disambiguation" | "review">("disambiguation");

    const tabs = [
        { id: "disambiguation" as const, label: t('page.authority.tab_groups') },
        { id: "review" as const, label: t('page.authority.tab_review_queue') },
    ];

    return (
        <div className="space-y-6">
            <PageHeader
                breadcrumbs={[{ label: "Home", href: "/" }, { label: t('page.authority.breadcrumb') }]}
                title={t('page.authority.title')}
                description={t('page.authority.description')}
            />

            <TabNav
                tabs={tabs}
                activeTab={tab}
                onTabChange={(id) => setTab(id as "disambiguation" | "review")}
            />

            {tab === "disambiguation" && <DisambiguationTab activeDomain={activeDomain} />}
            {tab === "review" && <ReviewQueueTab activeDomain={activeDomain} />}
        </div>
    );
}
