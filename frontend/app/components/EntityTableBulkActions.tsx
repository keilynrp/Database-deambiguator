"use client";

import React from "react";
import { useLanguage } from "../contexts/LanguageContext";

export interface EntityTableBulkActionsProps {
    selectedCount: number;
    pageSelectionOnly?: boolean;
    bulkEnriching: boolean;
    bulkDeleting: boolean;
    onBulkEnrich: () => void;
    onBulkExport: () => void;
    onBulkDelete: () => void;
    onClearSelection: () => void;
}

export function EntityTableBulkActions({
    selectedCount,
    pageSelectionOnly = true,
    bulkEnriching,
    bulkDeleting,
    onBulkEnrich,
    onBulkExport,
    onBulkDelete,
    onClearSelection,
}: EntityTableBulkActionsProps) {
    const { t } = useLanguage();
    if (selectedCount === 0) return null;

    return (
        <div className="toast-enter fixed bottom-6 left-1/2 z-[150] -translate-x-1/2">
            <div className="flex items-center gap-3 rounded-2xl border border-gray-200 bg-white px-5 py-3 shadow-xl dark:border-gray-700 dark:bg-gray-900">
                <span className="inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                    {selectedCount}
                </span>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300 pr-1">
                    {pageSelectionOnly
                        ? t("page.entity_table.bulk_selected_page", { count: selectedCount })
                        : t("page.entity_table.bulk_selected", { count: selectedCount })}
                </span>
                {pageSelectionOnly && (
                    <span className="hidden text-xs text-gray-400 lg:inline">
                        {t("page.entity_table.bulk_page_scope_hint")}
                    </span>
                )}
                <div className="h-4 w-px bg-gray-200 dark:bg-gray-700" />
                <button
                    onClick={onBulkEnrich}
                    disabled={bulkEnriching}
                    className="flex items-center gap-1.5 rounded-lg bg-purple-50 px-3 py-1.5 text-xs font-semibold text-purple-700 transition-colors hover:bg-purple-100 disabled:opacity-60 dark:bg-purple-500/10 dark:text-purple-400 dark:hover:bg-purple-500/20"
                >
                    {bulkEnriching ? (
                        <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                    ) : (
                        <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                        </svg>
                    )}
                    {t("page.entity_table.bulk_enrich_action")}
                </button>
                <button
                    onClick={onBulkExport}
                    className="flex items-center gap-1.5 rounded-lg bg-green-50 px-3 py-1.5 text-xs font-semibold text-green-700 transition-colors hover:bg-green-100 dark:bg-green-500/10 dark:text-green-400 dark:hover:bg-green-500/20"
                >
                    <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                    {t("page.entity_table.bulk_export_action")}
                </button>
                <button
                    onClick={onBulkDelete}
                    disabled={bulkDeleting}
                    className="flex items-center gap-1.5 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-700 transition-colors hover:bg-red-100 disabled:opacity-60 dark:bg-red-500/10 dark:text-red-400 dark:hover:bg-red-500/20"
                >
                    {bulkDeleting ? (
                        <svg className="h-3.5 w-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                    ) : (
                        <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
                        </svg>
                    )}
                    {t("common.delete")}
                </button>
                <div className="h-4 w-px bg-gray-200 dark:bg-gray-700" />
                <button
                    onClick={onClearSelection}
                    className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-gray-800"
                    title={t("page.entity_table.clear_selection")}
                >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
        </div>
    );
}

export default EntityTableBulkActions;
