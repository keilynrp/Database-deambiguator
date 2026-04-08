"use client";

import { useLanguage } from "../contexts/LanguageContext";
import type { ActiveFacets } from "./FacetPanel";

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

    return (
        <>
            {hasActiveFacets && (
                <div className="mb-2 flex flex-wrap gap-1.5 px-1">
                    {Object.entries(activeFacets)
                        .filter(([, value]) => value)
                        .map(([field, value]) => (
                            <span
                                key={field}
                                className="inline-flex items-center gap-1 rounded-full border border-indigo-200 bg-indigo-100 px-2 py-0.5 text-xs text-indigo-800 dark:border-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                            >
                                <span className="font-medium">{field.replace(/_/g, " ")}:</span> {value}
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
