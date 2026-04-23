"use client";

import type React from "react";
import Link from "next/link";
import { useLanguage } from "../contexts/LanguageContext";
import { Badge, ErrorBanner, QualityBadge, SkeletonTableBody } from "./ui";
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
            return parsedJson.journal ?? "";
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
    const thClass = "px-5 py-3.5 text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400";
    const inputClass =
        "h-8 w-full rounded border border-gray-200 bg-white px-2 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    return (
        <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <div
                ref={scrollContainerRef}
                className="table-container"
                style={shouldVirtualize ? { maxHeight: viewportHeight, overflowY: "auto" } : undefined}
                onScroll={shouldVirtualize ? (event) => onScrollTopChange(event.currentTarget.scrollTop) : undefined}
            >
                <table className="w-full min-w-[1200px] text-left text-sm">
                    <thead className={shouldVirtualize ? "sticky top-0 z-10 bg-white dark:bg-gray-900" : undefined}>
                        <tr className="border-b border-gray-200 dark:border-gray-800">
                            <th className="w-10 px-4 py-3.5">
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
                            </th>
                            <th className={`${thClass} no-wrap w-16`}>{t("page.entity_table.id")}</th>
                            {activeDomain ? (
                                activeDomain.attributes.map((attribute) => (
                                    <th
                                        key={attribute.name}
                                        className={`${thClass} no-wrap`}
                                        title={
                                            attribute.name === "validation_status"
                                                ? t("page.entity_table.review_status_help")
                                                : undefined
                                        }
                                    >
                                        {CORE_ATTRIBUTE_LABEL_KEYS[attribute.name]
                                            ? t(CORE_ATTRIBUTE_LABEL_KEYS[attribute.name])
                                            : attribute.label}
                                    </th>
                                ))
                            ) : (
                                <th className={`${thClass} no-wrap`}>{t("entities.primary_label")}</th>
                            )}
                            <th
                                className={`${thClass} no-wrap`}
                                title={t("page.entity_table.system_status_help")}
                            >
                                {t("page.entity_table.system_status")}
                            </th>
                            <th
                                className={`${thClass} no-wrap cursor-pointer select-none`}
                                onClick={onSortQuality}
                                title={t("page.entity_table.sort_quality")}
                            >
                                {t("entities.quality")} {sortBy === "quality_score" ? (sortOrder === "desc" ? "↓" : "↑") : ""}
                            </th>
                            <th className={`${thClass} no-wrap text-right`}>{t("common.actions")}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                        {fetchError ? (
                            <tr>
                                <td colSpan={11} className="px-5">
                                    <ErrorBanner variant="row" message={t("page.entity_table.failed_load")} detail={fetchError} onRetry={onRetry} />
                                </td>
                            </tr>
                        ) : loading ? (
                            <SkeletonTableBody rows={limit} cols={7} />
                        ) : entities.length === 0 ? (
                            <tr>
                                <td colSpan={11} className="px-5 py-12 text-center">
                                    <div className="flex flex-col items-center gap-2">
                                        <svg className="h-10 w-10 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={1.5}
                                                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"
                                            />
                                        </svg>
                                        <span className="text-sm text-gray-500 dark:text-gray-400">{t("entities.empty")}</span>
                                    </div>
                                </td>
                            </tr>
                        ) : (
                            <>
                                {paddingTop > 0 && (
                                    <tr>
                                        <td colSpan={99} style={{ height: paddingTop, padding: 0 }} />
                                    </tr>
                                )}
                                {visibleEntities.map((entity) => {
                                    const isEditing = editingId === entity.id;
                                    const parsedJson = parseNormalizedJson(entity.normalized_json);

                                    if (isEditing) {
                                        return (
                                            <tr key={entity.id} className="bg-blue-50/50 dark:bg-blue-500/5">
                                                <td className="w-10 px-4 py-2.5" />
                                                <td className="px-5 py-2.5 text-gray-500 dark:text-gray-400">{entity.id}</td>
                                                {activeDomain ? (
                                                    activeDomain.attributes.map((attribute) => {
                                                        const value = resolveAttributeValue(entity, parsedJson, attribute.name, attribute.is_core);
                                                        const isEditableCoreField = attribute.is_core && attribute.name in editData;

                                                        return (
                                                            <td key={attribute.name} className="px-5 py-2.5">
                                                                <input
                                                                    className={inputClass}
                                                                    value={String(value ?? "")}
                                                                    onChange={(event) => {
                                                                        if (isEditableCoreField) {
                                                                            onEditDataChange({
                                                                                ...editData,
                                                                                [attribute.name]: event.target.value,
                                                                            });
                                                                        }
                                                                    }}
                                                                    disabled={!isEditableCoreField}
                                                                    title={!isEditableCoreField ? t("page.entity_table.extended_attributes_readonly") : ""}
                                                                />
                                                            </td>
                                                        );
                                                    })
                                                ) : (
                                                    <td className="px-5 py-2.5">
                                                        <input
                                                            className={inputClass}
                                                            value={editData.primary_label || ""}
                                                            onChange={(event) =>
                                                                onEditDataChange({ ...editData, primary_label: event.target.value })
                                                            }
                                                        />
                                                    </td>
                                                )}
                                                <td className="px-5 py-2.5">
                                                    <select
                                                        className={inputClass}
                                                        value={editData.validation_status ?? ""}
                                                        onChange={(event) =>
                                                            onEditDataChange({ ...editData, validation_status: event.target.value })
                                                        }
                                                    >
                                                        <option value="pending">{t("page.entity_table.status_pending")}</option>
                                                        <option value="valid">{t("page.entity_table.status_valid")}</option>
                                                        <option value="invalid">{t("page.entity_table.status_invalid")}</option>
                                                    </select>
                                                </td>
                                                <td className="px-5 py-2.5">
                                                    <QualityBadge score={entity.quality_score} />
                                                </td>
                                                <td className="px-5 py-2.5">
                                                    <div className="flex items-center justify-end gap-1">
                                                        <button
                                                            onClick={onSaveEdit}
                                                            disabled={saving}
                                                            className="rounded-lg p-1.5 text-green-600 hover:bg-green-100 disabled:opacity-50 dark:text-green-400 dark:hover:bg-green-500/10"
                                                            title={t("common.save")}
                                                        >
                                                            {saving ? (
                                                                <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                                </svg>
                                                            ) : (
                                                                <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                                                </svg>
                                                            )}
                                                        </button>
                                                        <button
                                                            onClick={onCancelEdit}
                                                            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"
                                                            title={t("common.cancel")}
                                                        >
                                                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                                            </svg>
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    }

                                    return (
                                        <tr
                                            key={entity.id}
                                            className={`group transition-colors hover:bg-gray-50 dark:hover:bg-gray-800/50 ${
                                                selectedIds.has(entity.id) ? "bg-blue-50/60 dark:bg-blue-500/5" : ""
                                            }`}
                                        >
                                            <td className="w-10 px-4 py-3.5">
                                                <input
                                                    type="checkbox"
                                                    className="h-4 w-4 rounded border-gray-300 accent-blue-600"
                                                    checked={selectedIds.has(entity.id)}
                                                    onChange={() => onToggleSelect(entity.id)}
                                                    aria-label={`${t("page.entity_table.select_entity")} ${entity.id}`}
                                                />
                                            </td>
                                            <td className="px-5 py-3.5 text-gray-500 dark:text-gray-400">{entity.id}</td>
                                            {activeDomain ? (
                                                activeDomain.attributes.map((attribute) => {
                                                    const value = resolveAttributeValue(entity, parsedJson, attribute.name, attribute.is_core);

                                                    return (
                                                        <td key={attribute.name} className="px-5 py-3.5 text-gray-600 dark:text-gray-300">
                                                            {renderLocalizedValue(attribute.name, value, t("page.entity_table.empty_value"), t)}
                                                        </td>
                                                    );
                                                })
                                            ) : (
                                                <td className="px-5 py-3.5 font-medium text-gray-900 dark:text-white">{entity.primary_label}</td>
                                            )}
                                            <td className="px-5 py-3.5">
                                                {(() => {
                                                    const statusMeta = enrichmentBadgeMeta(entity.enrichment_status, t);
                                                    return (
                                                        <Badge variant={statusMeta.variant}>
                                                            {statusMeta.label}
                                                        </Badge>
                                                    );
                                                })()}
                                            </td>
                                            <td className="px-5 py-3.5">
                                                <QualityBadge score={entity.quality_score} />
                                            </td>
                                            <td className="px-5 py-3.5">
                                                <div className="flex items-center justify-end gap-1 opacity-0 transition-opacity group-hover:opacity-100">
                                                    <button
                                                        onClick={() => onSelectEntity(entity)}
                                                        className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                                                        title={t("page.entity_table.quick_view")}
                                                    >
                                                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                                        </svg>
                                                    </button>
                                                    <Link
                                                        href={`/entities/${entity.id}`}
                                                        className="rounded-lg p-1.5 text-gray-400 hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-500/10 dark:hover:text-blue-400"
                                                        title={t("page.entity_table.view_full_details")}
                                                    >
                                                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
                                                        </svg>
                                                    </Link>
                                                    <button
                                                        onClick={() => onStartEdit(entity)}
                                                        className="rounded-lg p-1.5 text-gray-400 hover:bg-blue-100 hover:text-blue-600 dark:hover:bg-blue-500/10 dark:hover:text-blue-400"
                                                        title={t("common.edit")}
                                                    >
                                                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
                                                        </svg>
                                                    </button>
                                                    <button
                                                        onClick={() => onDeleteEntity(entity)}
                                                        disabled={deletingId === entity.id}
                                                        className="rounded-lg p-1.5 text-gray-400 hover:bg-red-100 hover:text-red-600 disabled:opacity-50 dark:hover:bg-red-500/10 dark:hover:text-red-400"
                                                        title={t("common.delete")}
                                                    >
                                                        {deletingId === entity.id ? (
                                                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                            </svg>
                                                        ) : (
                                                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.11 0 00-7.5 0" />
                                                            </svg>
                                                        )}
                                                    </button>
                                                    <button
                                                        onClick={() => onEnrichEntity(entity.id)}
                                                        disabled={enrichingId === entity.id}
                                                        className="rounded-lg p-1.5 text-gray-400 hover:bg-purple-100 hover:text-purple-600 disabled:opacity-50 dark:hover:bg-purple-500/10 dark:hover:text-purple-400"
                                                        title={t("page.entity_table.enrich_entity")}
                                                    >
                                                        {enrichingId === entity.id ? (
                                                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                                                            </svg>
                                                        ) : (
                                                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                                                            </svg>
                                                        )}
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    );
                                })}
                                {paddingBottom > 0 && (
                                    <tr>
                                        <td colSpan={99} style={{ height: paddingBottom, padding: 0 }} />
                                    </tr>
                                )}
                            </>
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
