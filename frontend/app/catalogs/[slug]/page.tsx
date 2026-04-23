"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { EmptyState, ErrorBanner, PageHeader, StatCard } from "../../components/ui";
import { useLanguage } from "../../contexts/LanguageContext";

interface CatalogPortal {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  domain_id: string;
  visibility: string;
  search: string | null;
  min_quality: number | null;
  ft_entity_type: string | null;
  ft_validation_status: string | null;
  ft_enrichment_status: string | null;
  ft_source: string | null;
  default_sort: string;
  default_order: string;
  featured_facets: string[];
  summary?: {
    total_records: number;
    enriched_records: number;
    enriched_pct: number;
    avg_quality: number | null;
  };
}

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
}

interface CatalogResultsPayload {
  portal: CatalogPortal;
  filters: Record<string, string | number | null>;
  total: number;
  skip: number;
  limit: number;
  items: CatalogRecord[];
  facets: Record<string, { value: string; count: number }[]>;
}

function parseAttributes(raw: string | null): Record<string, unknown> {
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export default function CatalogPortalPage() {
  const { slug } = useParams<{ slug: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { t } = useLanguage();
  const tr = (key: string, fallback: string) => {
    const value = t(key);
    return value === key ? fallback : value;
  };

  const [portal, setPortal] = useState<CatalogPortal | null>(null);
  const [results, setResults] = useState<CatalogResultsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState(searchParams.get("search") ?? "");
  const [selectedFacets, setSelectedFacets] = useState<Record<string, string>>({
    ft_entity_type: searchParams.get("ft_entity_type") ?? "",
    ft_validation_status: searchParams.get("ft_validation_status") ?? "",
    ft_enrichment_status: searchParams.get("ft_enrichment_status") ?? "",
    ft_source: searchParams.get("ft_source") ?? "",
  });

  const currentPage = Number(searchParams.get("page") || "1");
  const limit = 24;

  const loadPortal = async () => {
    setLoading(true);
    setError(null);
    try {
      const portalRes = await apiFetch(`/catalogs/${slug}`);
      if (!portalRes.ok) throw new Error(`HTTP ${portalRes.status}`);
      const portalPayload = await portalRes.json();
      setPortal(portalPayload);

      const query = new URLSearchParams({
        skip: String((currentPage - 1) * limit),
        limit: String(limit),
      });
      if (search) query.set("search", search);
      Object.entries(selectedFacets).forEach(([key, value]) => {
        if (value) query.set(key, value);
      });

      const resultsRes = await apiFetch(`/catalogs/${slug}/results?${query.toString()}`);
      if (!resultsRes.ok) throw new Error(`HTTP ${resultsRes.status}`);
      setResults(await resultsRes.json());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : tr("catalogs.portal_load_failed", "Failed to load the catalog portal."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPortal();
  }, [slug, currentPage]);

  const totalPages = useMemo(() => {
    if (!results) return 1;
    return Math.max(1, Math.ceil(results.total / results.limit));
  }, [results]);

  const applyFilters = () => {
    const next = new URLSearchParams();
    if (search) next.set("search", search);
    Object.entries(selectedFacets).forEach(([key, value]) => {
      if (value) next.set(key, value);
    });
    next.set("page", "1");
    router.replace(`/catalogs/${slug}?${next.toString()}`);
    void loadPortal();
  };

  const goToPage = (page: number) => {
    const next = new URLSearchParams(searchParams.toString());
    next.set("page", String(page));
    router.replace(`/catalogs/${slug}?${next.toString()}`);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: tr("nav.home", "Knowledge Explorer"), href: "/" },
          { label: tr("nav.catalogs", "Catalog Portals"), href: "/catalogs" },
          { label: portal?.title || slug },
        ]}
        title={portal?.title || tr("catalogs.portal_title_loading", "Catalog portal")}
        description={portal?.description || tr("catalogs.portal_subtitle", "A lighter discovery view over the current workspace scope.")}
      />

      {error && <ErrorBanner message={error} />}

      {portal?.summary && (
        <div className="grid gap-4 md:grid-cols-3">
          <StatCard
            icon={<span className="text-lg">#</span>}
            label={tr("catalogs.summary.total", "Records")}
            value={portal.summary.total_records.toLocaleString()}
            subtitle={tr("catalogs.summary.total_hint", "Items currently inside this portal scope")}
          />
          <StatCard
            icon={<span className="text-lg">+</span>}
            label={tr("catalogs.summary.enriched", "Enriched")}
            value={`${portal.summary.enriched_pct.toFixed(1)}%`}
            subtitle={`${portal.summary.enriched_records.toLocaleString()} ${tr("catalogs.summary.enriched_hint", "records already enriched")}`}
          />
          <StatCard
            icon={<span className="text-lg">Q</span>}
            label={tr("catalogs.summary.quality", "Average quality")}
            value={portal.summary.avg_quality !== null ? portal.summary.avg_quality.toFixed(2) : "—"}
            subtitle={tr("catalogs.summary.quality_hint", "Use this as a quick signal before sharing broadly")}
          />
        </div>
      )}

      <section className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="space-y-4 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-600 dark:text-blue-400">
              {tr("catalogs.filters_eyebrow", "Search and refine")}
            </p>
            <h2 className="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
              {tr("catalogs.filters_title", "Catalog filters")}
            </h2>
          </div>

          <label className="block space-y-2 text-sm text-gray-700 dark:text-gray-300">
            <span>{tr("catalogs.field.search", "Search")}</span>
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
              placeholder={tr("catalogs.field.search_placeholder", "CRISPR, education, materials science...")}
            />
          </label>

          {results && Object.entries(results.facets).map(([field, options]) => (
            <label key={field} className="block space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span className="capitalize">{field.replaceAll("_", " ")}</span>
              <select
                value={selectedFacets[field] || ""}
                onChange={(event) => setSelectedFacets((prev) => ({ ...prev, [field]: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
              >
                <option value="">{tr("catalogs.filters.any", "Any")}</option>
                {options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.value} ({option.count})
                  </option>
                ))}
              </select>
            </label>
          ))}

          <button
            onClick={applyFilters}
            className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
          >
            {tr("catalogs.filters.apply", "Apply filters")}
          </button>
        </aside>

        <section className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {results
                  ? tr("catalogs.results_count", "{count} records in this portal").replace("{count}", results.total.toLocaleString())
                  : tr("catalogs.results_loading", "Loading records...")}
              </p>
            </div>
            <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
              {portal?.domain_id || "—"}
            </span>
          </div>

          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <div key={index} className="h-28 animate-pulse rounded-2xl bg-gray-100 dark:bg-gray-800" />
              ))}
            </div>
          ) : results && results.items.length > 0 ? (
            <div className="space-y-4">
              {results.items.map((record) => {
                const attributes = parseAttributes(record.attributes_json);
                const journal = (attributes.journal as string | undefined) || "—";
                const year = attributes.year as string | number | undefined;
                return (
                  <Link
                    key={record.id}
                    href={`/catalogs/${slug}/record/${record.id}`}
                    className="block rounded-2xl border border-gray-200 p-4 transition hover:border-blue-300 hover:bg-blue-50/40 dark:border-gray-800 dark:hover:border-blue-700 dark:hover:bg-blue-950/20"
                  >
                    <div className="flex flex-wrap items-start justify-between gap-4">
                      <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                          {record.primary_label || tr("common.no_data", "No data")}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {record.secondary_label || tr("catalogs.record.no_author", "Author data not available")}
                        </p>
                        <div className="flex flex-wrap gap-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>{journal}</span>
                          <span>•</span>
                          <span>{year || "—"}</span>
                          <span>•</span>
                          <span>{record.canonical_id || "—"}</span>
                        </div>
                      </div>
                      <div className="space-y-2 text-right">
                        <div className="text-sm font-medium text-gray-700 dark:text-gray-200">
                          {tr("catalogs.record.citations", "Citations")}: {(record.enrichment_citation_count ?? 0).toLocaleString()}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {tr("catalogs.record.quality", "Quality")}: {record.quality_score !== null && record.quality_score !== undefined ? record.quality_score.toFixed(2) : "—"}
                        </div>
                      </div>
                    </div>
                  </Link>
                );
              })}

              <div className="flex items-center justify-between border-t border-gray-200 pt-4 dark:border-gray-800">
                <button
                  onClick={() => goToPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage <= 1}
                  className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                >
                  {tr("catalogs.pagination.previous", "Previous")}
                </button>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {tr("catalogs.pagination.page", "Page")} {currentPage} / {totalPages}
                </span>
                <button
                  onClick={() => goToPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage >= totalPages}
                  className="rounded-xl border border-gray-200 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                >
                  {tr("catalogs.pagination.next", "Next")}
                </button>
              </div>
            </div>
          ) : (
            <EmptyState
              icon="search"
              color="blue"
              title={tr("catalogs.results_empty_title", "No records match these filters")}
              description={tr("catalogs.results_empty_description", "Try a broader query or remove one of the active filters to recover results.")}
            />
          )}
        </section>
      </section>
    </div>
  );
}
