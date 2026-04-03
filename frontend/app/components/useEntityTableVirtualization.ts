"use client";

import { useMemo } from "react";
import type { Entity } from "./EntityTable.types";

interface UseEntityTableVirtualizationOptions {
    entities: Entity[];
    editingId: number | null;
    scrollTop: number;
    virtualThreshold?: number;
    rowHeight?: number;
    viewportHeight?: number;
    overscan?: number;
}

export function useEntityTableVirtualization({
    entities,
    editingId,
    scrollTop,
    virtualThreshold = 50,
    rowHeight = 52,
    viewportHeight = 620,
    overscan = 5,
}: UseEntityTableVirtualizationOptions) {
    return useMemo(() => {
        const shouldVirtualize = entities.length > virtualThreshold;
        const editIdx = editingId !== null ? entities.findIndex((entity) => entity.id === editingId) : -1;
        let visStart = shouldVirtualize ? Math.max(0, Math.floor(scrollTop / rowHeight) - overscan) : 0;
        let visEnd = shouldVirtualize
            ? Math.min(entities.length, Math.ceil((scrollTop + viewportHeight) / rowHeight) + overscan)
            : entities.length;

        if (editIdx >= 0) {
            visStart = Math.min(visStart, editIdx);
            visEnd = Math.max(visEnd, editIdx + 1);
        }

        return {
            shouldVirtualize,
            visibleEntities: entities.slice(visStart, visEnd),
            paddingTop: shouldVirtualize ? visStart * rowHeight : 0,
            paddingBottom: shouldVirtualize ? (entities.length - visEnd) * rowHeight : 0,
            viewportHeight,
        };
    }, [editingId, entities, overscan, rowHeight, scrollTop, viewportHeight, virtualThreshold]);
}
