"use client";

import { useLanguage } from "../contexts/LanguageContext";
import type { ActiveFacets } from "./FacetPanel";

const FIELD_LABELS: Record<string, string> = {
    entity_type: "page.import.field.entity_type",
    domain: "page.import.field.domain",
    validation_status: "page.entity_table.review_status",
    enrichment_status: "page.entity_table.system_status",
    source: "page.exec_dashboard.source",
};

export interface EntityTableToolbarProps {
    activeFacets: ActiveFacets;
    search: string;
    minQuality: string;
    page: number;
    onSearchChange: (value: string) => void;
    onMinQualityChange: (value: string) => void;
    onClearFacet: (field: string) => void;
}

export default function EntityTableToolbar({
    activeFacets,
    search,
    minQuality,
    page,
    onSearchChange,
    onMinQualityChange,
    onClearFacet,
}: EntityTableToolbarProps) {
    const { t } = useLanguage();
    const hasActiveFacets = Object.entries(activeFacets).some(([, value]) => value);
    const hasToolbarFilters = hasActiveFacets || Boolean(search) || Boolean(minQuality);
    const formatFacetField = (field: string) => {
        const key = FIELD_LABELS[field];
        if (!key) return field.replace(/_/g, " ");
        const translated = t(key);
        return translated === key ? field.replace(/_/g, " ") : translated;
    };
    const formatFacetValue = (field: string, value: string) => {
        if (field === "entity_type") {
            const translated = t(`page.authority.entity_type_${value}`);
            return translated === `page.authority.entity_type_${value}` ? value : translated;
        }
        if (field === "validation_status") {
            const translated = t(`page.entity_table.status_${value}`);
            return translated === `page.entity_table.status_${value}` ? value : translated;
        }
        if (field === "enrichment_status") {
            const enrichmentKeyMap: Record<string, string> = {
                completed: "entities.filter.enriched",
                pending: "entities.filter.pending",
                processing: "page.entity_table.status_processing",
                failed: "entities.filter.failed",
                none: "page.entity_table.status_not_started",
            };
            const key = enrichmentKeyMap[value] ?? `entities.filter.${value}`;
            const translated = t(key);
            return translated === key ? value : translated;
        }
        return value;
    };

    return (
        <>
            {hasToolbarFilters && (
                <div className="mb-2 flex flex-wrap gap-1.5 px-1">
                    {search && (
                        <span className="inline-flex items-center gap-1 rounded-full border border-sky-200 bg-sky-100 px-2 py-0.5 text-xs text-sky-800 dark:border-sky-700 dark:bg-sky-900/40 dark:text-sky-300">
                            <span className="font-medium">{t("common.search")}:</span> {search}
                            <button
                                onClick={() => onSearchChange("")}
                                className="ml-0.5 font-bold leading-none hover:text-sky-600"
                            >
                                x
                            </button>
                        </span>
                    )}
                    {minQuality && (
                        <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-100 px-2 py-0.5 text-xs text-emerald-800 dark:border-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300">
                            <span className="font-medium">{t("page.entity_table.min_quality")}:</span>
                            {minQuality === "0.7" ? "70%+" : minQuality === "0.3" ? "30%+" : t("page.entity_table.under_30")}
                            <button
                                onClick={() => onMinQualityChange("")}
                                className="ml-0.5 font-bold leading-none hover:text-emerald-600"
                            >
                                x
                            </button>
                        </span>
                    )}
                    {Object.entries(activeFacets)
                        .filter(([, value]) => value)
                        .map(([field, value]) => (
                            <span
                                key={field}
                                className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-100 px-2 py-0.5 text-xs text-indigo-800 dark:border-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                            >
                                <span className="font-medium">{formatFacetField(field)}:</span> {formatFacetValue(field, value)}
                                <button
                                    onClick={() => onClearFacet(field)}
                                    className="ml-0.5 font-bold leading-none hover:text-indigo-600"
                                >
                                    x
                                </button>
                            </span>
                        ))}
                </div>
            )}

            <div className="flex flex-wrap items-center justify-between gap-3">
                <div className="flex flex-wrap items-center gap-3">
                    <div className="relative">
                        <svg
                            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                            />
                        </svg>
                        <input
                            type="text"
                            placeholder={t("entities.search_placeholder")}
                            className="h-10 w-80 rounded-lg border border-gray-200 bg-white pl-10 pr-4 text-sm text-gray-700 placeholder-gray-400 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:placeholder-gray-500 dark:focus:border-blue-500"
                            value={search}
                            onChange={(event) => onSearchChange(event.target.value)}
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">{t("page.entity_table.min_quality")}:</label>
                        <select
                            value={minQuality}
                            onChange={(event) => onMinQualityChange(event.target.value)}
                            className="h-10 rounded-lg border border-gray-200 bg-white px-2 text-sm text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                        >
                            <option value="">{t("common.all")}</option>
                            <option value="0.7">70%+</option>
                            <option value="0.3">30%+</option>
                            <option value="0.0">{t("page.entity_table.under_30")}</option>
                        </select>
                    </div>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">{t("common.page")} {page + 1}</span>
            </div>
        </>
    );
}
