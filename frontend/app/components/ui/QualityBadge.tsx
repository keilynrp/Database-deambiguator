"use client";

import React from "react";

export function QualityBadge({ score }: { score: number | null | undefined }) {
    if (score === null || score === undefined) return <span className="text-xs text-gray-400">—</span>;
    const pct = Math.round(score * 100);
    const color = score >= 0.7 ? "bg-emerald-500" : score >= 0.3 ? "bg-amber-400" : "bg-red-500";
    return (
        <div className="flex items-center gap-1.5">
            <div className="w-16 h-1.5 rounded-full bg-gray-200 dark:bg-gray-700">
                <div className={`h-1.5 rounded-full ${color}`} style={{ width: `${pct}%` }} />
            </div>
            <span className="text-xs tabular-nums text-gray-600 dark:text-gray-400">{pct}%</span>
        </div>
    );
}

export default QualityBadge;
