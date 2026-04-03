"use client";

import MonteCarloChart from "./MonteCarloChart";
import type { Entity } from "./EntityTable.types";

export interface EntityTableDetailsModalProps {
    entity: Entity | null;
    onClose: () => void;
}

export default function EntityTableDetailsModal({ entity, onClose }: EntityTableDetailsModalProps) {
    if (!entity) return null;

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
            <div className="flex h-[90vh] w-full max-w-4xl flex-col rounded-2xl bg-white shadow-2xl dark:bg-gray-900">
                <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">{entity.primary_label}</h2>
                        <p className="text-sm text-gray-500">Full details and attributes</p>
                    </div>
                    <button onClick={onClose} className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2">
                        {Object.entries(entity).map(([key, value]) => {
                            if (key === "id" || key === "normalized_json") return null;

                            const label = key
                                .split("_")
                                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                                .join(" ");

                            return (
                                <div key={key} className="flex flex-col gap-1 border-b border-gray-50 pb-2 dark:border-gray-800/50">
                                    <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{label}</span>
                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                        {value !== null && value !== "" ? String(value) : <span className="italic text-gray-300">No data</span>}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                    {entity.enrichment_status === "completed" && (
                        <div className="mt-8 rounded-xl border border-purple-100 bg-white p-5 shadow-sm dark:border-purple-500/10 dark:bg-gray-800/50">
                            <MonteCarloChart productId={entity.id} />
                        </div>
                    )}
                </div>
                <div className="border-t border-gray-100 px-6 py-4 dark:border-gray-800">
                    <button
                        onClick={onClose}
                        className="w-full rounded-xl bg-gray-100 py-2.5 text-sm font-semibold text-gray-900 transition-colors hover:bg-gray-200 dark:bg-gray-800 dark:text-white dark:hover:bg-gray-700"
                    >
                        Close Details
                    </button>
                </div>
            </div>
        </div>
    );
}
