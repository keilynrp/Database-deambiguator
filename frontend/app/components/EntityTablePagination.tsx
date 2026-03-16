"use client";

import React from "react";

export interface EntityTablePaginationProps {
    totalEntitiesVisible: number;
    limit: number;
    page: number;
    loading: boolean;
    onLimitChange: (limit: number) => void;
    onPageChange: (updater: number | ((prev: number) => number)) => void;
}

export function EntityTablePagination({
    totalEntitiesVisible,
    limit,
    page,
    loading,
    onLimitChange,
    onPageChange
}: EntityTablePaginationProps) {
    return (
        <div className="flex items-center justify-between border-t border-gray-200 px-5 py-3.5 dark:border-gray-800">
            <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500 dark:text-gray-400">Rows per page:</span>
                <select
                    value={limit}
                    onChange={(e) => {
                        onLimitChange(Number(e.target.value));
                        onPageChange(0);
                    }}
                    className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-sm text-gray-700 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-300"
                >
                    <option value={10}>10</option>
                    <option value={20}>20</option>
                    <option value={50}>50</option>
                    <option value={100}>100</option>
                    <option value={200}>200</option>
                </select>
            </div>

            <div className="flex items-center gap-4">
                <button
                    onClick={() => onPageChange(p => Math.max(0, p - 1))}
                    disabled={page === 0 || loading}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3.5 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                    Previous
                </button>
                <div className="flex items-center gap-2">
                    <span className="inline-flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-sm font-medium text-white">
                        {page + 1}
                    </span>
                </div>
                <button
                    // If the number of visible entities in this run is less than limit, we are likely on the last page.
                    onClick={() => onPageChange(p => p + 1)}
                    disabled={totalEntitiesVisible < limit || loading}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 px-3.5 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-40 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                    Next
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                </button>
            </div>
        </div>
    );
}

export default EntityTablePagination;
