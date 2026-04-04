"use client";

import { useCallback, useEffect, useState } from "react";
import { useToast } from "../components/ui";
import { apiFetch } from "@/lib/api";
import type { DomainAttribute, DomainSchema } from "../contexts/DomainContext";
import ReviewQueueControls from "./ReviewQueueControls";
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
            <ReviewQueueControls
                activeDomain={activeDomain}
                queueMode={queueMode}
                statusFilter={statusFilter}
                fieldFilter={fieldFilter}
                authorRouteFilter={authorRouteFilter}
                authorReviewFilter={authorReviewFilter}
                authorNilOnly={authorNilOnly}
                batchField={batchField}
                batchEntityType={batchEntityType}
                batchLimit={batchLimit}
                resolving={resolving}
                resolveResult={resolveResult}
                acting={acting}
                selectedCount={selected.size}
                summary={summary}
                onQueueModeChange={setQueueMode}
                onStatusFilterChange={setStatusFilter}
                onFieldFilterChange={setFieldFilter}
                onAuthorRouteFilterChange={setAuthorRouteFilter}
                onAuthorReviewFilterChange={setAuthorReviewFilter}
                onAuthorNilOnlyChange={setAuthorNilOnly}
                onBatchFieldChange={setBatchField}
                onBatchEntityTypeChange={setBatchEntityType}
                onBatchLimitChange={setBatchLimit}
                onBatchResolve={batchResolve}
                onBulkAction={bulkAction}
            />

            <ReviewQueueSummaryPanels
                queueMode={queueMode}
                summary={summary}
                authorSummary={authorSummary}
                authorMetrics={authorMetrics}
            />

            <div className="rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
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

