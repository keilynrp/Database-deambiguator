"use client";

import { useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "../contexts/LanguageContext";

export interface FacetValue { value: string; count: number; }
export interface FacetData { [field: string]: FacetValue[]; }
export interface ActiveFacets { [field: string]: string | null; }

const FIELD_LABELS: Record<string, string> = {
  entity_type:       "page.import.field.entity_type",
  domain:            "page.import.field.domain",
  validation_status: "page.import.field.validation_status",
  enrichment_status: "entities.enrichment_status",
  source:            "page.exec_dashboard.source",
};

// Color chips per field for visual identity
const FIELD_COLORS: Record<string, string> = {
  entity_type:       "bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300",
  domain:            "bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300",
  validation_status: "bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300",
  enrichment_status: "bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300",
  source:            "bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300",
};

interface FacetPanelProps {
  activeFacets: ActiveFacets;
  onFacetChange: (field: string, value: string | null) => void;
  refreshKey?: number; // increment to trigger re-fetch
}

export default function FacetPanel({ activeFacets, onFacetChange, refreshKey }: FacetPanelProps) {
  const { t } = useLanguage();
  const [facets, setFacets] = useState<FacetData>({});
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);

  const fetchFacets = useCallback(async () => {
    try {
      const res = await apiFetch("/entities/facets");
      if (res.ok) setFacets(await res.json());
    } catch { /* non-critical */ } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchFacets(); }, [fetchFacets, refreshKey]);

  const toggleCollapse = (field: string) =>
    setCollapsed(prev => ({ ...prev, [field]: !prev[field] }));

  const activeCount = Object.values(activeFacets).filter(Boolean).length;

  const translateFacetLabel = (field: string) => {
    const key = FIELD_LABELS[field];
    return key ? t(key) : field;
  };

  const translateFacetValue = (field: string, value: string) => {
    if (!value) return t("page.entity_table.empty_value");

    if (field === "entity_type") {
      const translated = t(`page.authority.entity_type_${value}`);
      return translated === `page.authority.entity_type_${value}` ? value : translated;
    }

    if (field === "validation_status") {
      const statusKey = `page.entity_table.status_${value}`;
      const translated = t(statusKey);
      return translated === statusKey ? value : translated;
    }

    if (field === "enrichment_status") {
      const translated = t(`entities.filter.${value}`);
      return translated === `entities.filter.${value}` ? value : translated;
    }

    return value;
  };

  return (
    <aside className="flex flex-col gap-2">
      {/* Header */}
      <div className="flex items-center justify-between px-1 mb-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">
          {t("page.facets.filter_by")}
        </span>
        {activeCount > 0 && (
          <button
            onClick={() => Object.keys(activeFacets).forEach(f => onFacetChange(f, null))}
            className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
          >
            {t("page.facets.clear_all", { count: activeCount })}
          </button>
        )}
      </div>

      {loading && (
        <div className="text-xs text-gray-400 px-1 animate-pulse">{t("page.facets.loading")}</div>
      )}

      {Object.entries(FIELD_LABELS).map(([field]) => {
        const values = facets[field] ?? [];
        if (values.length === 0) return null;
        const isCollapsed = collapsed[field];
        const active = activeFacets[field];
        const chipColor = FIELD_COLORS[field] ?? "bg-gray-100 text-gray-700";

        return (
          <div
            key={field}
            className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden"
          >
            {/* Section header */}
            <button
              onClick={() => toggleCollapse(field)}
              className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
            >
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{translateFacetLabel(field)}</span>
              <span className="text-gray-400 text-xs">{isCollapsed ? "▸" : "▾"}</span>
            </button>

            {/* Values list */}
            {!isCollapsed && (
              <ul className="px-2 pb-2 space-y-0.5">
                {values.slice(0, 8).map(({ value, count }) => {
                  const isActive = active === value;
                  return (
                    <li key={value}>
                      <button
                        onClick={() => onFacetChange(field, isActive ? null : value)}
                        className={`w-full flex items-center justify-between px-2 py-1 rounded text-left text-xs transition-colors ${
                          isActive
                            ? "bg-indigo-600 text-white font-medium"
                            : "hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300"
                        }`}
                        >
                        <span className="truncate max-w-[110px]">{translateFacetValue(field, value)}</span>
                        <span
                          className={`ml-1 flex-shrink-0 rounded-full px-1.5 py-0 text-[10px] font-mono ${
                            isActive ? "bg-white/20 text-white" : chipColor
                          }`}
                        >
                          {count}
                        </span>
                      </button>
                    </li>
                  );
                })}
                {values.length > 8 && (
                  <li className="text-[10px] text-gray-400 px-2 pt-0.5">
                    {t("page.facets.read_more", { count: values.length - 8 })}
                  </li>
                )}
              </ul>
            )}
          </div>
        );
      })}
    </aside>
  );
}
