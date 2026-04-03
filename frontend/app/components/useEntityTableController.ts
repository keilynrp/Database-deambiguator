"use client";

import { useCallback, useEffect, useState } from "react";
import type { ActiveFacets } from "./FacetPanel";
import type { EditableFields, Entity } from "./EntityTable.types";
import { apiFetch } from "@/lib/api";

interface UseEntityTableControllerOptions {
    toast: (message: string, variant?: string) => void;
}

export function useEntityTableController({ toast }: UseEntityTableControllerOptions) {
    const [entities, setEntities] = useState<Entity[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState("");
    const [debouncedSearch, setDebouncedSearch] = useState("");
    const [page, setPage] = useState(0);
    const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
    const [limit, setLimit] = useState(20);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editData, setEditData] = useState<EditableFields>({
        primary_label: "",
        secondary_label: "",
        canonical_id: "",
        entity_type: "",
        domain: "",
        validation_status: "",
    });
    const [saving, setSaving] = useState(false);
    const [enrichingId, setEnrichingId] = useState<number | null>(null);
    const [minQuality, setMinQuality] = useState<string>("");
    const [sortBy, setSortBy] = useState<string>("id");
    const [sortOrder, setSortOrder] = useState<string>("asc");
    const [deletingId, setDeletingId] = useState<number | null>(null);
    const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
    const [bulkDeleting, setBulkDeleting] = useState(false);
    const [bulkEnriching, setBulkEnriching] = useState(false);
    const [fetchError, setFetchError] = useState<string | null>(null);
    const [activeFacets, setActiveFacets] = useState<ActiveFacets>({});
    const [scrollTop, setScrollTop] = useState(0);

    useEffect(() => {
        const handler = setTimeout(() => {
            setDebouncedSearch(search);
            setPage(0);
        }, 500);

        return () => clearTimeout(handler);
    }, [search]);

    const fetchEntities = useCallback(async () => {
        setLoading(true);
        setSelectedIds(new Set());
        setFetchError(null);

        try {
            const queryParams = new URLSearchParams({
                skip: (page * limit).toString(),
                limit: limit.toString(),
                sort_by: sortBy,
                order: sortOrder,
            });

            if (debouncedSearch) queryParams.append("search", debouncedSearch);
            if (minQuality) queryParams.append("min_quality", minQuality);
            if (activeFacets.entity_type) queryParams.append("ft_entity_type", activeFacets.entity_type);
            if (activeFacets.domain) queryParams.append("ft_domain", activeFacets.domain);
            if (activeFacets.validation_status) queryParams.append("ft_validation_status", activeFacets.validation_status);
            if (activeFacets.enrichment_status) queryParams.append("ft_enrichment_status", activeFacets.enrichment_status);
            if (activeFacets.source) queryParams.append("ft_source", activeFacets.source);

            const res = await apiFetch(`/entities?${queryParams}`);
            if (!res.ok) throw new Error(`Server responded with ${res.status}`);
            setEntities(await res.json());
        } catch (error) {
            const message = error instanceof Error ? error.message : "Unknown error";
            setFetchError(message);
        } finally {
            setLoading(false);
        }
    }, [debouncedSearch, page, limit, minQuality, sortBy, sortOrder, activeFacets]);

    useEffect(() => {
        fetchEntities();
    }, [fetchEntities]);

    function handleFacetChange(field: string, value: string | null) {
        setActiveFacets((prev) => ({ ...prev, [field]: value }));
        setPage(0);
    }

    function startEdit(entity: Entity) {
        setEditingId(entity.id);
        setEditData({
            primary_label: entity.primary_label || "",
            secondary_label: entity.secondary_label || "",
            canonical_id: entity.canonical_id || "",
            entity_type: entity.entity_type || "",
            domain: entity.domain || "",
            validation_status: entity.validation_status || "pending",
        });
    }

    function cancelEdit() {
        setEditingId(null);
    }

    async function saveEdit() {
        if (!editingId) return;
        setSaving(true);

        try {
            const res = await apiFetch(`/entities/${editingId}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(editData),
            });
            if (!res.ok) throw new Error("Failed to update");
            const updated = await res.json();
            setEntities((prev) => prev.map((entity) => (entity.id === editingId ? updated : entity)));
            setEditingId(null);
        } catch {
            toast("Error updating entity", "error");
        } finally {
            setSaving(false);
        }
    }

    async function deleteEntity(id: number) {
        setDeletingId(id);
        try {
            const res = await apiFetch(`/entities/${id}`, { method: "DELETE" });
            if (!res.ok) throw new Error("Failed to delete");
            setEntities((prev) => prev.filter((entity) => entity.id !== id));
            toast("Entity deleted", "success");
        } catch {
            toast("Error deleting entity", "error");
        } finally {
            setDeletingId(null);
        }
    }

    async function enrichEntity(id: number) {
        setEnrichingId(id);
        try {
            const res = await apiFetch(`/enrich/row/${id}`, { method: "POST" });
            if (!res.ok) throw new Error("Failed to enrich");
            const enriched = await res.json();
            setEntities((prev) => prev.map((entity) => (entity.id === id ? { ...entity, ...enriched } : entity)));
            toast("Enrichment complete", "success");
        } catch {
            toast("Error enriching entity", "error");
        } finally {
            setEnrichingId(null);
        }
    }

    function toggleSelect(id: number) {
        setSelectedIds((prev) => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    }

    function toggleSelectAll() {
        if (selectedIds.size === entities.length) {
            setSelectedIds(new Set());
        } else {
            setSelectedIds(new Set(entities.map((entity) => entity.id)));
        }
    }

    async function handleBulkDelete() {
        if (!confirm(`Delete ${selectedIds.size} selected entities?`)) return;
        setBulkDeleting(true);
        try {
            const res = await apiFetch("/entities/bulk", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ids: Array.from(selectedIds) }),
            });
            if (!res.ok) throw new Error("Bulk delete failed");
            const data = await res.json();
            setEntities((prev) => prev.filter((entity) => !selectedIds.has(entity.id)));
            setSelectedIds(new Set());
            toast(`${data.deleted} entities deleted`, "success");
        } catch {
            toast("Bulk delete failed", "error");
        } finally {
            setBulkDeleting(false);
        }
    }

    async function handleBulkEnrich() {
        setBulkEnriching(true);
        try {
            const res = await apiFetch("/enrich/bulk-ids", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ ids: Array.from(selectedIds) }),
            });
            if (!res.ok) throw new Error("Bulk enrich failed");
            const data = await res.json();
            toast(`${data.queued} entities queued for enrichment`, "success");
            setSelectedIds(new Set());
        } catch {
            toast("Bulk enrich failed", "error");
        } finally {
            setBulkEnriching(false);
        }
    }

    function handleBulkExport() {
        const selected = entities.filter((entity) => selectedIds.has(entity.id));
        const headers = [
            "id",
            "primary_label",
            "secondary_label",
            "canonical_id",
            "entity_type",
            "domain",
            "validation_status",
            "enrichment_status",
            "source",
        ];
        const rows = selected.map((entity) =>
            headers
                .map((header) => {
                    const value = (entity as Record<string, unknown>)[header];
                    return value == null ? "" : `"${String(value).replace(/"/g, '""')}"`;
                })
                .join(","),
        );
        const csv = [headers.join(","), ...rows].join("\n");
        const blob = new Blob([csv], { type: "text/csv" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `entities_selection_${selected.length}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        toast(`${selected.length} entities exported as CSV`, "success");
    }

    return {
        entities,
        loading,
        search,
        setSearch,
        page,
        setPage,
        selectedEntity,
        setSelectedEntity,
        limit,
        setLimit,
        editingId,
        editData,
        setEditData,
        saving,
        enrichingId,
        minQuality,
        setMinQuality,
        sortBy,
        setSortBy,
        sortOrder,
        setSortOrder,
        deletingId,
        selectedIds,
        bulkDeleting,
        bulkEnriching,
        fetchError,
        activeFacets,
        handleFacetChange,
        fetchEntities,
        startEdit,
        cancelEdit,
        saveEdit,
        deleteEntity,
        enrichEntity,
        toggleSelect,
        toggleSelectAll,
        handleBulkDelete,
        handleBulkEnrich,
        handleBulkExport,
        scrollTop,
        setScrollTop,
    };
}
