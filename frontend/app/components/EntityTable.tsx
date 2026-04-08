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
    const facetRefreshKey = 0;
    const {
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
        setSelectedIds,
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
    } = useEntityTableController({ toast });
    const scrollContainerRef = useRef<HTMLDivElement>(null);

    const { shouldVirtualize, visibleEntities, paddingTop, paddingBottom, viewportHeight } = useEntityTableVirtualization({
        entities,
        editingId,
        scrollTop,
    });

    return (
        <div className="grid items-start gap-5 lg:grid-cols-[16rem_minmax(0,1fr)]">
            <FacetPanel activeFacets={activeFacets} onFacetChange={handleFacetChange} refreshKey={facetRefreshKey} />
            <div className="min-w-0">
                <div className="space-y-6">
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

                    <EntityTableDetailsModal entity={selectedEntity} onClose={() => setSelectedEntity(null)} />

                    <EntityTablePagination
                        totalEntitiesVisible={entities.length}
                        limit={limit}
                        page={page}
                        loading={loading}
                        onLimitChange={setLimit}
                        onPageChange={setPage}
                    />

                    <EntityTableBulkActions
                        selectedCount={selectedIds.size}
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
