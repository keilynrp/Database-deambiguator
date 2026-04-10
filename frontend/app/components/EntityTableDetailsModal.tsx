"use client";

import { useLanguage } from "../contexts/LanguageContext";
import type { EntityTableDomain } from "./EntityTable.types";
import MonteCarloChart from "./MonteCarloChart";
import type { Entity } from "./EntityTable.types";

export interface EntityTableDetailsModalProps {
    entity: Entity | null;
    activeDomain: EntityTableDomain;
    onClose: () => void;
}

const CORE_FIELD_LABEL_KEYS: Record<string, string> = {
    primary_label: "entities.primary_label",
    secondary_label: "page.import.field.secondary_label",
    canonical_id: "page.import.field.canonical_id",
    entity_type: "page.import.field.entity_type",
    domain: "page.import.field.domain",
    validation_status: "page.import.field.validation_status",
};

const SYSTEM_FIELDS: Array<{ key: keyof Entity; labelKey: string }> = [
    { key: "enrichment_status", labelKey: "entities.enrichment_status" },
    { key: "source", labelKey: "page.exec_dashboard.source" },
    { key: "enrichment_citation_count", labelKey: "page.import.field.enrichment_citation_count" },
    { key: "quality_score", labelKey: "entities.quality" },
];

function parseJsonObject(raw: string | null): Record<string, unknown> {
    if (!raw) return {};
    try {
        return JSON.parse(raw) as Record<string, unknown>;
    } catch {
        return {};
    }
}

function titleCaseKey(key: string): string {
    return key
        .split("_")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ");
}

function formatValue(value: unknown, emptyLabel: string): string {
    if (value === null || value === undefined || value === "") return emptyLabel;
    if (Array.isArray(value)) return value.join(", ");
    if (typeof value === "object") return JSON.stringify(value);
    return String(value);
}

export default function EntityTableDetailsModal({ entity, activeDomain, onClose }: EntityTableDetailsModalProps) {
    const { t } = useLanguage();
    if (!entity) return null;

    const normalizedAttributes = parseJsonObject(entity.normalized_json);
    const sourceAttributes = parseJsonObject(entity.attributes_json);
    const mergedExtendedAttributes = { ...sourceAttributes, ...normalizedAttributes };

    const coreFields = activeDomain
        ? activeDomain.attributes.filter((attribute) => attribute.is_core).map((attribute) => ({
            label: CORE_FIELD_LABEL_KEYS[attribute.name] ? t(CORE_FIELD_LABEL_KEYS[attribute.name]) : attribute.label,
            value: entity[attribute.name as keyof Entity],
          }))
        : [
            { label: t("entities.primary_label"), value: entity.primary_label },
            { label: t("page.import.field.secondary_label"), value: entity.secondary_label },
            { label: t("page.import.field.canonical_id"), value: entity.canonical_id },
            { label: t("page.import.field.entity_type"), value: entity.entity_type },
            { label: t("page.import.field.domain"), value: entity.domain },
        ];

    const systemFields = SYSTEM_FIELDS.map((field) => ({
        label: t(field.labelKey),
        value: entity[field.key],
    }));

    const extendedFields = Object.entries(mergedExtendedAttributes)
        .filter(([, value]) => value !== null && value !== undefined && value !== "")
        .map(([key, value]) => ({
            label: activeDomain?.attributes.find((attribute) => attribute.name === key)?.label ?? titleCaseKey(key),
            value,
        }));

    return (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm">
            <div className="flex h-[90vh] w-full max-w-4xl flex-col rounded-2xl bg-white shadow-2xl dark:bg-gray-900">
                <div className="flex items-center justify-between border-b border-gray-100 px-6 py-4 dark:border-gray-800">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white">{entity.primary_label}</h2>
                        <p className="text-sm text-gray-500">{t("page.entity_table.full_details")}</p>
                    </div>
                    <button onClick={onClose} className="rounded-lg p-2 hover:bg-gray-100 dark:hover:bg-gray-800">
                        <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                <div className="flex-1 overflow-y-auto p-6">
                    <div className="space-y-8">
                        <section>
                            <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">{t("page.entity_table.section_core")}</h3>
                            <div className="grid grid-cols-1 gap-x-8 gap-y-4 md:grid-cols-2">
                                {coreFields.map((field) => (
                                    <div key={field.label} className="flex flex-col gap-1 border-b border-gray-50 pb-2 dark:border-gray-800/50">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{field.label}</span>
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                            {formatValue(field.value, t("common.no_data"))}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </section>

                        <section>
                            <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">{t("page.entity_table.section_system")}</h3>
                            <div className="grid grid-cols-1 gap-x-8 gap-y-4 md:grid-cols-2">
                                {systemFields.map((field) => (
                                    <div key={field.label} className="flex flex-col gap-1 border-b border-gray-50 pb-2 dark:border-gray-800/50">
                                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{field.label}</span>
                                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                            {formatValue(field.value, t("common.no_data"))}
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </section>

                        {extendedFields.length > 0 && (
                            <section>
                                <h3 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">{t("page.entity_table.section_extended")}</h3>
                                <div className="grid grid-cols-1 gap-x-8 gap-y-4 md:grid-cols-2">
                                    {extendedFields.map((field) => (
                                        <div key={field.label} className="flex flex-col gap-1 border-b border-gray-50 pb-2 dark:border-gray-800/50">
                                            <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">{field.label}</span>
                                            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                                                {formatValue(field.value, t("common.no_data"))}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </section>
                        )}
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
                        {t("page.entity_table.close_details")}
                    </button>
                </div>
            </div>
        </div>
    );
}
