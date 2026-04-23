"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { ErrorBanner, PageHeader } from "../../../../components/ui";
import { useLanguage } from "../../../../contexts/LanguageContext";

interface CatalogRecord {
  id: number;
  primary_label: string | null;
  secondary_label: string | null;
  canonical_id: string | null;
  entity_type: string | null;
  domain: string | null;
  validation_status: string | null;
  enrichment_status: string | null;
  enrichment_citation_count: number | null;
  quality_score: number | null;
  source: string | null;
  attributes_json: string | null;
  normalized_json: string | null;
}

function parseJson(raw: string | null): Record<string, unknown> {
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "—";
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export default function CatalogRecordPage() {
  const { slug, id } = useParams<{ slug: string; id: string }>();
  const { t } = useLanguage();
  const tr = (key: string, fallback: string) => {
    const value = t(key);
    return value === key ? fallback : value;
  };

  const [record, setRecord] = useState<CatalogRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadRecord = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await apiFetch(`/catalogs/${slug}/records/${id}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        setRecord(await res.json());
      } catch (loadError) {
        setError(loadError instanceof Error ? loadError.message : tr("catalogs.record_load_failed", "Failed to load this catalog record."));
      } finally {
        setLoading(false);
      }
    };
    void loadRecord();
  }, [slug, id]);

  const mergedAttributes = useMemo(() => {
    if (!record) return {};
    return {
      ...parseJson(record.attributes_json),
      ...parseJson(record.normalized_json),
    };
  }, [record]);

  const coreFields = record ? [
    { label: tr("entities.primary_label", "Primary label"), value: record.primary_label },
    { label: tr("page.import.field.secondary_label", "Secondary label"), value: record.secondary_label },
    { label: tr("page.import.field.canonical_id", "Canonical ID"), value: record.canonical_id },
    { label: tr("page.import.field.entity_type", "Entity type"), value: record.entity_type },
    { label: tr("page.import.field.domain", "Domain"), value: record.domain },
  ] : [];

  const systemFields = record ? [
    { label: tr("entities.enrichment_status", "System status"), value: record.enrichment_status },
    { label: tr("page.exec_dashboard.source", "Source"), value: record.source },
    { label: tr("page.import.field.enrichment_citation_count", "Citation count"), value: record.enrichment_citation_count },
    { label: tr("entities.quality", "Quality"), value: record.quality_score !== null && record.quality_score !== undefined ? record.quality_score.toFixed(2) : "—" },
    { label: tr("page.import.field.validation_status", "Validation status"), value: record.validation_status },
  ] : [];

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: tr("nav.home", "Knowledge Explorer"), href: "/" },
          { label: tr("nav.catalogs", "Catalog Portals"), href: "/catalogs" },
          { label: slug, href: `/catalogs/${slug}` },
          { label: record?.primary_label || tr("catalogs.record_title_loading", "Record detail") },
        ]}
        title={record?.primary_label || tr("catalogs.record_title_loading", "Catalog record")}
        description={tr("catalogs.record_subtitle", "Expanded record metadata for a friendlier, catalog-style consultation flow.")}
      />

      {error && <ErrorBanner message={error} />}

      {loading && (
        <div className="grid gap-4 md:grid-cols-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="h-24 animate-pulse rounded-2xl bg-gray-100 dark:bg-gray-800" />
          ))}
        </div>
      )}

      {record && (
        <>
          <div className="flex items-center justify-between">
            <Link
              href={`/catalogs/${slug}`}
              className="inline-flex items-center rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
            >
              ← {tr("catalogs.back_to_results", "Back to results")}
            </Link>
          </div>

          <section className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                {tr("catalogs.record.section_core", "Core record")}
              </h2>
              <div className="mt-4 space-y-4">
                {coreFields.map((field) => (
                  <div key={field.label} className="border-b border-gray-100 pb-3 dark:border-gray-800">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400">{field.label}</p>
                    <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{formatValue(field.value)}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                {tr("catalogs.record.section_system", "System signals")}
              </h2>
              <div className="mt-4 space-y-4">
                {systemFields.map((field) => (
                  <div key={field.label} className="border-b border-gray-100 pb-3 dark:border-gray-800">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400">{field.label}</p>
                    <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{formatValue(field.value)}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              {tr("catalogs.record.section_extended", "Extended metadata")}
            </h2>
            <div className="mt-5 grid gap-x-8 gap-y-4 md:grid-cols-2">
              {Object.entries(mergedAttributes).length > 0 ? (
                Object.entries(mergedAttributes).map(([key, value]) => (
                  <div key={key} className="border-b border-gray-100 pb-3 dark:border-gray-800">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400">
                      {key.replaceAll("_", " ")}
                    </p>
                    <p className="mt-1 text-sm text-gray-700 dark:text-gray-300 break-words">
                      {formatValue(value)}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {tr("catalogs.record.no_extended", "No extended metadata was stored for this record.")}
                </p>
              )}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
