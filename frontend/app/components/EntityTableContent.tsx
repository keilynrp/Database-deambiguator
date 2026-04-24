"use client";

import type React from "react";
import Link from "next/link";
import { useLanguage } from "../contexts/LanguageContext";
import { Badge, ErrorBanner, QualityBadge } from "./ui";
import RecordResultCard from "./RecordResultCard";
import type { EntityTableDomain, EditableFields, Entity } from "./EntityTable.types";

function parseNormalizedJson(normalizedJson: string | null): Record<string, unknown> {
    if (!normalizedJson) return {};

    try {
        return JSON.parse(normalizedJson) as Record<string, unknown>;
    } catch {
        return {};
    }
}

function resolveAttributeValue(
    entity: Entity,
    parsedJson: Record<string, unknown>,
    attributeName: string,
    isCore: boolean,
): unknown {
    if (!isCore) {
        return parsedJson[attributeName] ?? "";
    }

    const directValue = entity[attributeName as keyof Entity];
    if (directValue !== undefined && directValue !== null && directValue !== "") {
        return directValue;
    }

    switch (attributeName) {
        case "title":
            return entity.primary_label ?? parsedJson.title ?? "";
        case "authors":
            return parsedJson.authors ?? entity.secondary_label ?? "";
        case "doi":
            return entity.canonical_id ?? parsedJson.doi ?? "";
        case "journal":
            return parsedJson.journal ?? parsedJson.venue ?? "";
        case "year":
            return parsedJson.year ?? "";
        case "citations":
            return entity.enrichment_citation_count ?? parsedJson.citation_count ?? "";
        default:
            return parsedJson[attributeName] ?? "";
    }
}

function renderDisplayValue(attributeName: string, value: unknown, emptyLabel: string) {
    if (value === null || value === "") {
        return <span className="text-gray-400">{emptyLabel}</span>;
    }

    if (attributeName === "canonical_id" || attributeName === "doi") {
        return (
            <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-700 dark:bg-gray-800 dark:text-gray-300">
                {String(value)}
            </code>
        );
    }

    return String(value);
}

function renderLocalizedValue(
    attributeName: string,
    value: unknown,
    emptyLabel: string,
    t: (key: string, params?: Record<string, string | number>) => string,
) {
    if (attributeName === "validation_status" && typeof value === "string" && value) {
        const statusKey = `page.entity_table.status_${value}`;
        const translated = t(statusKey);
        return translated === statusKey ? value : translated;
    }

    if (attributeName === "enrichment_status" && typeof value === "string" && value) {
        const enrichmentKeyMap: Record<string, string> = {
            completed: "entities.filter.enriched",
            pending: "entities.filter.pending",
            processing: "page.entity_table.status_processing",
            failed: "entities.filter.failed",
            none: "page.entity_table.status_not_started",
        };
        const translationKey = enrichmentKeyMap[value];
        if (!translationKey) return value;
        const translated = t(translationKey);
        return translated === translationKey ? value : translated;
    }

    return renderDisplayValue(attributeName, value, emptyLabel);
}

const CORE_ATTRIBUTE_LABEL_KEYS: Record<string, string> = {
    primary_label: "entities.primary_label",
    secondary_label: "page.import.field.secondary_label",
    canonical_id: "page.import.field.canonical_id",
    entity_type: "page.import.field.entity_type",
    domain: "page.import.field.domain",
    validation_status: "page.entity_table.review_status",
};

function enrichmentBadgeMeta(
    status: string | null,
    t: (key: string, params?: Record<string, string | number>) => string,
): { label: string; variant: "success" | "warning" | "error" | "default" } {
    switch (status) {
        case "completed":
            return { label: t("entities.filter.enriched"), variant: "success" };
        case "pending":
            return { label: t("entities.filter.pending"), variant: "warning" };
        case "processing":
            return { label: t("page.entity_table.status_processing"), variant: "warning" };
        case "failed":
            return { label: t("entities.filter.failed"), variant: "error" };
        case "none":
        case null:
        default:
            return { label: t("page.entity_table.status_not_started"), variant: "default" };
    }
}

export interface EntityTableContentProps {
    activeDomain: EntityTableDomain;
    entities: Entity[];
    visibleEntities: Entity[];
    loading: boolean;
    limit: number;
    fetchError: string | null;
    shouldVirtualize: boolean;
    viewportHeight: number;
    paddingTop: number;
    paddingBottom: number;
    selectedIds: Set<number>;
    editingId: number | null;
    editData: EditableFields;
    saving: boolean;
    deletingId: number | null;
    enrichingId: number | null;
    portalByBatchId: Record<number, string>;
    sortBy: string;
    sortOrder: string;
    scrollContainerRef: React.RefObject<HTMLDivElement | null>;
    onScrollTopChange: (value: number) => void;
    onToggleSelectAll: () => void;
    onToggleSelect: (id: number) => void;
    onSortQuality: () => void;
    onRetry: () => void;
    onStartEdit: (entity: Entity) => void;
    onCancelEdit: () => void;
    onSaveEdit: () => void;
    onEditDataChange: (next: EditableFields) => void;
    onSelectEntity: (entity: Entity) => void;
    onDeleteEntity: (entity: Entity) => void;
    onEnrichEntity: (id: number) => void;
}

export default function EntityTableContent({
    activeDomain,
    entities,
    visibleEntities,
    loading,
    limit,
    fetchError,
    shouldVirtualize,
    viewportHeight,
    paddingTop,
    paddingBottom,
    selectedIds,
    editingId,
    editData,
    saving,
    deletingId,
    enrichingId,
    portalByBatchId,
    sortBy,
    sortOrder,
    scrollContainerRef,
    onScrollTopChange,
    onToggleSelectAll,
    onToggleSelect,
    onSortQuality,
    onRetry,
    onStartEdit,
    onCancelEdit,
    onSaveEdit,
    onEditDataChange,
    onSelectEntity,
    onDeleteEntity,
    onEnrichEntity,
}: EntityTableContentProps) {
    const { t } = useLanguage();
    const inputClass =
        "h-10 w-full rounded-xl border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";
    const activeAttributes = activeDomain?.attributes ?? [];
    const summaryAttributes = activeAttributes.filter((attribute) => !["title", "authors", "primary_label", "secondary_label"].includes(attribute.name));
    const sourceLabel = (() => {
        const translated = t("page.exec_dashboard.source");
        return translated === "page.exec_dashboard.source" ? "Source" : translated;
    })();

    return (
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div
                ref={scrollContainerRef}
                className="divide-y divide-gray-100 dark:divide-gray-800"
                style={shouldVirtualize ? { maxHeight: viewportHeight, overflowY: "auto" } : undefined}
                onScroll={shouldVirtualize ? (event) => onScrollTopChange(event.currentTarget.scrollTop) : undefined}
            >
                <div className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b border-gray-200 bg-white/95 px-4 py-3 backdrop-blur dark:border-gray-800 dark:bg-gray-900/95">
                    <label className="flex items-center gap-3 text-sm text-gray-600 dark:text-gray-300">
                        <input
                            type="checkbox"
                            className="h-4 w-4 rounded border-gray-300 accent-blue-600"
                            checked={entities.length > 0 && selectedIds.size === entities.length}
                            ref={(element) => {
                                if (element) {
                                    element.indeterminate = selectedIds.size > 0 && selectedIds.size < entities.length;
                                }
                            }}
                            onChange={onToggleSelectAll}
                            aria-label={t("page.entity_table.select_all")}
                        />
                        <span className="font-medium text-gray-900 dark:text-white">{entities.length.toLocaleString()}</span>
                    </label>
                    <button
                        onClick={onSortQuality}
                        className="rounded-xl border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                        title={t("page.entity_table.sort_quality")}
                    >
                        {t("entities.quality")} {sortBy === "quality_score" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
                    </button>
                </div>

                {fetchError ? (
                    <div className="p-4">
                        <ErrorBanner variant="row" message={t("page.entity_table.failed_load")} detail={fetchError} onRetry={onRetry} />
                    </div>
                ) : loading ? (
                    <div className="space-y-4 p-4">
                        {Array.from({ length: limit }).map((_, index) => (
                            <div key={index} className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-950">
                                <div className="flex animate-pulse gap-4">
                                    <div className="h-16 w-16 rounded-2xl bg-gray-100 dark:bg-gray-800" />
                                    <div className="flex-1 space-y-3">
                                        <div className="h-4 w-2/3 rounded bg-gray-100 dark:bg-gray-800" />
                                        <div className="h-3 w-1/2 rounded bg-gray-100 dark:bg-gray-800" />
                                        <div className="grid gap-2 sm:grid-cols-3">
                                            <div className="h-10 rounded-xl bg-gray-100 dark:bg-gray-800" />
                                            <div className="h-10 rounded-xl bg-gray-100 dark:bg-gray-800" />
                                            <div className="h-10 rounded-xl bg-gray-100 dark:bg-gray-800" />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : entities.length === 0 ? (
                    <div className="px-5 py-12 text-center">
                        <div className="flex flex-col items-center gap-2">
                            <svg className="h-10 w-10 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                            </svg>
                            <span className="text-sm text-gray-500 dark:text-gray-400">{t("entities.empty")}</span>
                        </div>
                    </div>
                ) : (
                    <>
                        {paddingTop > 0 && <div style={{ height: paddingTop }} />}
                        <div className="divide-y divide-gray-100 dark:divide-gray-800">
                            {visibleEntities.map((entity) => {
                                const isEditing = editingId === entity.id;
                                const parsedJson = parseNormalizedJson(entity.normalized_json);
                                const titleValue = String(resolveAttributeValue(entity, parsedJson, "title", true) || entity.primary_label || t("page.entity_table.unnamed_entity"));
                                const secondaryValue = resolveAttributeValue(entity, parsedJson, "authors", true) || resolveAttributeValue(entity, parsedJson, "secondary_label", true);
                                const identifierValue = resolveAttributeValue(entity, parsedJson, "doi", true) || resolveAttributeValue(entity, parsedJson, "canonical_id", true);
                                const journalValue = resolveAttributeValue(entity, parsedJson, "journal", true);
                                const yearValue = resolveAttributeValue(entity, parsedJson, "year", true);
                                const citationsValue = resolveAttributeValue(entity, parsedJson, "citations", true);
                                const sourceValue = parsedJson.source ?? entity.source ?? "";
                                const statusMeta = enrichmentBadgeMeta(entity.enrichment_status, t);
                                const portalSlug = entity.import_batch_id ? portalByBatchId[entity.import_batch_id] : undefined;

                                if (isEditing) {
                                    return (
                                        <div key={entity.id} className="bg-blue-50/50 p-4 dark:bg-blue-500/5">
                                            <div className="rounded-2xl border border-blue-200 bg-white p-4 shadow-sm dark:border-blue-900/40 dark:bg-gray-950">
                                                <div className="flex flex-wrap items-center justify-between gap-3">
                                                    <div>
                                                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">{t("common.edit")}</p>
                                                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">#{entity.id}</p>
                                                    </div>
                                                    <div className="flex items-center gap-2">
                                                        <QualityBadge score={entity.quality_score} />
                                                        <select
                                                            className={inputClass}
                                                            value={editData.validation_status ?? ""}
                                                            onChange={(event) => onEditDataChange({ ...editData, validation_status: event.target.value })}
                                                        >
                                                            <option value="pending">{t("page.entity_table.status_pending")}</option>
                                                            <option value="valid">{t("page.entity_table.status_valid")}</option>
                                                            <option value="invalid">{t("page.entity_table.status_invalid")}</option>
                                                        </select>
                                                    </div>
                                                </div>

                                                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                                                    {(activeAttributes.length > 0 ? activeAttributes : [{ name: "primary_label", label: t("entities.primary_label"), is_core: true }]).map((attribute) => {
                                                        const value = resolveAttributeValue(entity, parsedJson, attribute.name, attribute.is_core);
                                                        const isEditableCoreField = attribute.is_core && attribute.name in editData;
                                                        return (
                                                            <label key={attribute.name} className="space-y-2">
                                                                <span className="text-xs font-semibold uppercase tracking-[0.16em] text-gray-500 dark:text-gray-400">
                                                                    {CORE_ATTRIBUTE_LABEL_KEYS[attribute.name] ? t(CORE_ATTRIBUTE_LABEL_KEYS[attribute.name]) : attribute.label}
                                                                </span>
                                                                <input
                                                                    className={inputClass}
                                                                    value={String(value ?? "")}
                                                                    onChange={(event) => {
                                                                        if (isEditableCoreField) {
                                                                            onEditDataChange({ ...editData, [attribute.name]: event.target.value });
                                                                        }
                                                                    }}
                                                                    disabled={!isEditableCoreField}
                                                                    title={!isEditableCoreField ? t("page.entity_table.extended_attributes_readonly") : ""}
                                                                />
                                                            </label>
                                                        );
                                                    })}
                                                </div>

                                                <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
                                                    <button onClick={onCancelEdit} className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800">
                                                        {t("common.cancel")}
                                                    </button>
                                                    <button onClick={onSaveEdit} disabled={saving} className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70">
                                                        {saving ? `${t("common.save")}...` : t("common.save")}
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                }

                                return (
                                    <div key={entity.id} className={`p-4 ${selectedIds.has(entity.id) ? "bg-blue-50/60 dark:bg-blue-500/5" : ""}`}>
                                        <RecordResultCard
                                            leadingSlot={
                                                <div className="flex flex-col items-start gap-3">
                                                    <input
                                                        type="checkbox"
                                                        className="mt-1 h-4 w-4 rounded border-gray-300 accent-blue-600"
                                                        checked={selectedIds.has(entity.id)}
                                                        onChange={() => onToggleSelect(entity.id)}
                                                        aria-label={`${t("page.entity_table.select_entity")} ${entity.id}`}
                                                    />
                                                </div>
                                            }
                                            tileLabel={(entity.entity_type || entity.domain || "entity").slice(0, 3)}
                                            title={titleValue}
                                            idTag={<Badge variant="default">#{entity.id}</Badge>}
                                            secondaryLine={
                                                <>
                                                    {secondaryValue ? <span>{String(secondaryValue)}</span> : null}
                                                    {secondaryValue && (journalValue || yearValue) ? <span>·</span> : null}
                                                    {journalValue ? <span>{String(journalValue)}</span> : null}
                                                    {journalValue && yearValue ? <span>·</span> : null}
                                                    {yearValue ? <span>{String(yearValue)}</span> : null}
                                                </>
                                            }
                                            statusRow={
                                                <>
                                                    <Badge variant="default">{renderLocalizedValue("validation_status", entity.validation_status, t("page.entity_table.empty_value"), t)}</Badge>
                                                    <Badge variant={statusMeta.variant}>{statusMeta.label}</Badge>
                                                    <QualityBadge score={entity.quality_score} />
                                                    {entity.entity_type ? <Badge variant="default">{entity.entity_type}</Badge> : null}
                                                    {entity.domain ? <Badge variant="default">{entity.domain}</Badge> : null}
                                                </>
                                            }
                                            primaryMeta={[
                                                {
                                                    label: t("page.import.field.canonical_id"),
                                                    value: renderDisplayValue("canonical_id", identifierValue, t("page.entity_table.empty_value")),
                                                    minWidthClassName: "min-w-[12rem]",
                                                },
                                                {
                                                    label: t("page.entity_table.system_status"),
                                                    value: <Badge variant={statusMeta.variant}>{statusMeta.label}</Badge>,
                                                },
                                                {
                                                    label: t("page.entity_table.review_status"),
                                                    value: renderLocalizedValue("validation_status", entity.validation_status, t("page.entity_table.empty_value"), t),
                                                },
                                                {
                                                    label: sourceLabel,
                                                    value: sourceValue ? String(sourceValue) : t("page.entity_table.empty_value"),
                                                },
                                            ]}
                                            secondaryMeta={summaryAttributes.slice(0, 6).map((attribute) => {
                                                const value = resolveAttributeValue(entity, parsedJson, attribute.name, attribute.is_core);
                                                return {
                                                    label: CORE_ATTRIBUTE_LABEL_KEYS[attribute.name] ? t(CORE_ATTRIBUTE_LABEL_KEYS[attribute.name]) : attribute.label,
                                                    value: renderLocalizedValue(attribute.name, value, t("page.entity_table.empty_value"), t),
                                                    minWidthClassName: "min-w-[12rem]",
                                                };
                                            })}
                                            actions={
                                                <>
                                                    <button onClick={() => onSelectEntity(entity)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800">
                                                        {t("page.entity_table.quick_view")}
                                                    </button>
                                                    <Link href={`/entities/${entity.id}`} className="rounded-xl border border-blue-200 px-3 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-50 dark:border-blue-900/40 dark:text-blue-300 dark:hover:bg-blue-950/30">
                                                        {t("page.entity_table.view_full_details")}
                                                    </Link>
                                                    {portalSlug ? (
                                                        <Link href={`/catalogs/${portalSlug}`} className="rounded-xl border border-emerald-200 px-3 py-2 text-sm font-medium text-emerald-700 transition hover:bg-emerald-50 dark:border-emerald-900/40 dark:text-emerald-300 dark:hover:bg-emerald-950/30">
                                                            Portal
                                                        </Link>
                                                    ) : null}
                                                    <button onClick={() => onStartEdit(entity)} className="rounded-xl border border-gray-200 px-3 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800">
                                                        {t("common.edit")}
                                                    </button>
                                                    <button onClick={() => onEnrichEntity(entity.id)} disabled={enrichingId === entity.id} className="rounded-xl border border-purple-200 px-3 py-2 text-sm font-medium text-purple-700 transition hover:bg-purple-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-purple-900/40 dark:text-purple-300 dark:hover:bg-purple-950/30">
                                                        {enrichingId === entity.id ? "..." : t("page.entity_table.enrich_entity")}
                                                    </button>
                                                    <button onClick={() => onDeleteEntity(entity)} disabled={deletingId === entity.id} className="rounded-xl border border-red-200 px-3 py-2 text-sm font-medium text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-red-900/40 dark:text-red-300 dark:hover:bg-red-950/30">
                                                        {deletingId === entity.id ? "..." : t("common.delete")}
                                                    </button>
                                                    {citationsValue !== null && citationsValue !== "" ? (
                                                        <div className="text-sm text-slate-600 dark:text-slate-300">
                                                            <span className="text-[11px] font-semibold uppercase tracking-[0.16em] text-slate-500 dark:text-slate-400">
                                                                Citations
                                                            </span>
                                                            <div className="mt-1">{String(citationsValue)}</div>
                                                        </div>
                                                    ) : null}
                                                </>
                                            }
                                        />
                                    </div>
                                );
                            })}
                        </div>
                        {paddingBottom > 0 && <div style={{ height: paddingBottom }} />}
                    </>
                )}
            </div>
        </div>
    );
}
