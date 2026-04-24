"use client";

import { useRef } from "react";
import { useDomain } from "../contexts/DomainContext";
import { useLanguage } from "../contexts/LanguageContext";
import { useToast } from "./ui";
import FacetPanel from "./FacetPanel";
import EntityTablePagination from "./EntityTablePagination";
import EntityTableBulkActions from "./EntityTableBulkActions";
import EntityTableToolbar from "./EntityTableToolbar";
import EntityTableContent from "./EntityTableContent";
import EntityTableDetailsModal from "./EntityTableDetailsModal";
import { useEntityTableController } from "./useEntityTableController";
import { useEntityTableVirtualization } from "./useEntityTableVirtualization";

export default function EntityTable() {
    const { activeDomain } = useDomain();
    const { t } = useLanguage();
    const { toast } = useToast();
    const {
        entities,
        totalCount,
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
        setSelectedIds,
        bulkDeleting,
        bulkEnriching,
        fetchError,
        activeFacets,
        facetRefreshKey,
        portalByBatchId,
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
    } = useEntityTableController({ toast });
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const { shouldVirtualize, visibleEntities, paddingTop, paddingBottom, viewportHeight } = useEntityTableVirtualization({
        entities,
        editingId,
        scrollTop,
    });

    return (
        <div className="grid items-start gap-5 lg:grid-cols-[16rem_minmax(0,1fr)]">
            <FacetPanel
                activeFacets={activeFacets}
                onFacetChange={handleFacetChange}
                search={search}
                minQuality={minQuality}
                refreshKey={facetRefreshKey}
            />
            <div className="min-w-0">
                <div className="space-y-6">
                    <div className="rounded-2xl border border-sky-200 bg-sky-50/80 px-4 py-4 shadow-sm dark:border-sky-900/40 dark:bg-sky-950/20">
                        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                            <div className="max-w-3xl">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-sky-700 dark:text-sky-400">
                                    {t("page.entity_table.guide.eyebrow")}
                                </p>
                                <h2 className="mt-2 text-sm font-semibold text-slate-900 dark:text-slate-100">
                                    {t("page.entity_table.guide.title")}
                                </h2>
                                <p className="mt-1 text-sm leading-6 text-slate-600 dark:text-slate-400">
                                    {t("page.entity_table.guide.description")}
                                </p>
                            </div>
                            <div className="grid gap-3 text-xs text-slate-600 dark:text-slate-400 sm:grid-cols-3 lg:max-w-xl">
                                <div className="rounded-xl border border-white/70 bg-white/80 px-3 py-3 dark:border-slate-800 dark:bg-slate-900/70">
                                    <p className="font-semibold text-slate-800 dark:text-slate-200">
                                        {t("page.entity_table.guide.system_status_title")}
                                    </p>
                                    <p className="mt-1">{t("page.entity_table.guide.system_status_body")}</p>
                                </div>
                                <div className="rounded-xl border border-white/70 bg-white/80 px-3 py-3 dark:border-slate-800 dark:bg-slate-900/70">
                                    <p className="font-semibold text-slate-800 dark:text-slate-200">
                                        {t("page.entity_table.guide.review_status_title")}
                                    </p>
                                    <p className="mt-1">{t("page.entity_table.guide.review_status_body")}</p>
                                </div>
                                <div className="rounded-xl border border-white/70 bg-white/80 px-3 py-3 dark:border-slate-800 dark:bg-slate-900/70">
                                    <p className="font-semibold text-slate-800 dark:text-slate-200">
                                        {t("page.entity_table.guide.quality_title")}
                                    </p>
                                    <p className="mt-1">{t("page.entity_table.guide.quality_body")}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <EntityTableToolbar
                        activeFacets={activeFacets}
                        search={search}
                        minQuality={minQuality}
                        page={page}
                        onSearchChange={setSearch}
                        onMinQualityChange={(value) => {
                            setMinQuality(value);
                            setPage(0);
                        }}
                        onClearFacet={(field) => handleFacetChange(field, null)}
                    />

                    <EntityTableContent
                        activeDomain={activeDomain}
                        entities={entities}
                        visibleEntities={visibleEntities}
                        loading={loading}
                        limit={limit}
                        fetchError={fetchError}
                        shouldVirtualize={shouldVirtualize}
                        viewportHeight={viewportHeight}
                        paddingTop={paddingTop}
                        paddingBottom={paddingBottom}
                        selectedIds={selectedIds}
                        editingId={editingId}
                        editData={editData}
                        saving={saving}
                        deletingId={deletingId}
                        enrichingId={enrichingId}
                        portalByBatchId={portalByBatchId}
                        sortBy={sortBy}
                        sortOrder={sortOrder}
                        scrollContainerRef={scrollContainerRef}
                        onScrollTopChange={setScrollTop}
                        onToggleSelectAll={toggleSelectAll}
                        onToggleSelect={toggleSelect}
                        onSortQuality={() => {
                            if (sortBy === "quality_score") {
                                setSortOrder((currentOrder) => (currentOrder === "asc" ? "desc" : "asc"));
                            } else {
                                setSortBy("quality_score");
                                setSortOrder("desc");
                            }
                            setPage(0);
                        }}
                        onRetry={fetchEntities}
                        onStartEdit={startEdit}
                        onCancelEdit={cancelEdit}
                        onSaveEdit={saveEdit}
                        onEditDataChange={setEditData}
                        onSelectEntity={setSelectedEntity}
                        onDeleteEntity={(entity) => {
                            if (confirm(t("page.entity_table.delete_single_confirm", {
                                id: entity.id,
                                label: entity.primary_label ?? t("page.entity_table.unnamed_entity"),
                            }))) {
                                deleteEntity(entity.id);
                            }
                        }}
                        onEnrichEntity={enrichEntity}
                    />

                    <EntityTableDetailsModal
                        entity={selectedEntity}
                        activeDomain={activeDomain}
                        onClose={() => setSelectedEntity(null)}
                    />

                    <EntityTablePagination
                        totalCount={totalCount}
                        limit={limit}
                        page={page}
                        loading={loading}
                        onLimitChange={setLimit}
                        onPageChange={setPage}
                    />

                    <EntityTableBulkActions
                        selectedCount={selectedIds.size}
                        pageSelectionOnly
                        bulkEnriching={bulkEnriching}
                        bulkDeleting={bulkDeleting}
                        onBulkEnrich={handleBulkEnrich}
                        onBulkExport={handleBulkExport}
                        onBulkDelete={handleBulkDelete}
                        onClearSelection={() => setSelectedIds(new Set())}
                    />
                </div>
            </div>
        </div>
    );
}
