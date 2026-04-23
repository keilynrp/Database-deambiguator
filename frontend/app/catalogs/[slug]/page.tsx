"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { EmptyState, ErrorBanner, PageHeader, StatCard } from "../../components/ui";
import { useLanguage } from "../../contexts/LanguageContext";
import { useAuth } from "../../contexts/AuthContext";

interface CatalogPortal {
  id: number;
  title: string;
  slug: string;
  description: string | null;
  domain_id: string;
  visibility: string;
  source_label: string | null;
  source_context: Record<string, string | number | boolean | null>;
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

async function readCatalogError(
  response: Response,
  fallback: string,
): Promise<string> {
  const payload = await response.json().catch(() => null);
  const detail =
    typeof payload?.detail === "string"
      ? payload.detail
      : typeof payload?.message === "string"
        ? payload.message
        : null;
  if (response.status === 404) {
    return fallback;
  }
  return detail || fallback;
}

function parseAttributes(raw: string | null): Record<string, unknown> {
  if (!raw) return {};
  try {
    return JSON.parse(raw) as Record<string, unknown>;
  } catch {
    return {};
  }
}

function visibilityTone(visibility: string | null | undefined): string {
  switch (visibility) {
    case "public":
      return "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300";
    case "org":
      return "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300";
    default:
      return "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300";
  }
}

export default function CatalogPortalPage() {
  const { slug } = useParams<{ slug: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const { t } = useLanguage();
  const { isAuthenticated } = useAuth();
  const tr = (key: string, fallback: string) => {
    const value = t(key);
    return value === key ? fallback : value;
  };
  const visibilityLabel = (visibility: string | null | undefined) => {
    switch (visibility) {
      case "public":
        return tr("catalogs.visibility.public", "Public read-only");
      case "org":
        return tr("catalogs.visibility.org", "Organization members");
      default:
        return tr("catalogs.visibility.private", "Private workspace");
    }
  };

  const [portal, setPortal] = useState<CatalogPortal | null>(null);
  const [results, setResults] = useState<CatalogResultsPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [search, setSearch] = useState(searchParams.get("search") ?? "");
  const [selectedFacets, setSelectedFacets] = useState<Record<string, string>>({
    ft_entity_type: searchParams.get("ft_entity_type") ?? "",
    ft_validation_status: searchParams.get("ft_validation_status") ?? "",
    ft_enrichment_status: searchParams.get("ft_enrichment_status") ?? "",
    ft_source: searchParams.get("ft_source") ?? "",
  });
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
    visibility: "private",
    source_label: "",
    search: "",
    min_quality: "",
    ft_entity_type: "",
    ft_validation_status: "",
    ft_enrichment_status: "",
    ft_source: "",
  });

  const currentPage = Number(searchParams.get("page") || "1");
  const limit = 24;

  const loadPortal = async () => {
    setLoading(true);
    setError(null);
    try {
      const portalRes = await apiFetch(`/catalogs/${slug}`);
      if (!portalRes.ok) {
        throw new Error(
          await readCatalogError(
            portalRes,
            tr("catalogs.portal_load_failed", "This catalog portal is not available right now."),
          ),
        );
      }
      const portalPayload = await portalRes.json();
      setPortal(portalPayload);
      setEditForm({
        title: portalPayload.title ?? "",
        description: portalPayload.description ?? "",
        visibility: portalPayload.visibility ?? "private",
        source_label: portalPayload.source_label ?? "",
        search: portalPayload.search ?? "",
        min_quality: portalPayload.min_quality !== null && portalPayload.min_quality !== undefined ? String(portalPayload.min_quality) : "",
        ft_entity_type: portalPayload.ft_entity_type ?? "",
        ft_validation_status: portalPayload.ft_validation_status ?? "",
        ft_enrichment_status: portalPayload.ft_enrichment_status ?? "",
        ft_source: portalPayload.ft_source ?? "",
      });

      const query = new URLSearchParams({
        skip: String((currentPage - 1) * limit),
        limit: String(limit),
      });
      if (search) query.set("search", search);
      Object.entries(selectedFacets).forEach(([key, value]) => {
        if (value) query.set(key, value);
      });

      const resultsRes = await apiFetch(`/catalogs/${slug}/results?${query.toString()}`);
      if (!resultsRes.ok) {
        throw new Error(
          await readCatalogError(
            resultsRes,
            tr("catalogs.results_load_failed", "The catalog results could not be loaded right now."),
          ),
        );
      }
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

  const savePortal = async () => {
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch(`/catalogs/${slug}`, {
        method: "PUT",
        body: JSON.stringify({
          title: editForm.title,
          description: editForm.description,
          visibility: editForm.visibility,
          source_label: editForm.source_label,
          search: editForm.search || null,
          min_quality: editForm.min_quality ? Number(editForm.min_quality) : null,
          ft_entity_type: editForm.ft_entity_type || null,
          ft_validation_status: editForm.ft_validation_status || null,
          ft_enrichment_status: editForm.ft_enrichment_status || null,
          ft_source: editForm.ft_source || null,
        }),
      });
      if (!res.ok) {
        throw new Error(
          await readCatalogError(
            res,
            tr("catalogs.update_failed", "Failed to update the catalog portal."),
          ),
        );
      }
      setEditing(false);
      await loadPortal();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : tr("catalogs.update_failed", "Failed to update the catalog portal."));
    } finally {
      setSaving(false);
    }
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
        actions={portal?.visibility === "public" ? (
          <a
            href={typeof window !== "undefined" ? window.location.href : `/catalogs/${slug}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center rounded-xl border border-blue-200 px-4 py-2 text-sm font-medium text-blue-700 transition hover:bg-blue-50 dark:border-blue-800 dark:text-blue-300 dark:hover:bg-blue-950/30"
          >
            {tr("catalogs.share.open_public", "Open public view")}
          </a>
        ) : undefined}
      />

      {error && <ErrorBanner message={error} />}

      {portal && (
        <section className="overflow-hidden rounded-[28px] border border-slate-200 bg-gradient-to-br from-slate-900 via-blue-950 to-cyan-950 text-white shadow-sm dark:border-slate-800">
          <div className="grid gap-6 px-6 py-6 lg:grid-cols-[1.2fr_0.8fr] lg:px-8 lg:py-8">
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.22em] text-cyan-100">
                  {tr("catalogs.hero.eyebrow", "Catalog portal")}
                </span>
                <span className={`rounded-full px-3 py-1 text-xs font-medium ${visibilityTone(portal.visibility)}`}>
                  {visibilityLabel(portal.visibility)}
                </span>
                <span className="rounded-full bg-white/10 px-3 py-1 text-xs font-medium text-slate-100">
                  {portal.domain_id}
                </span>
              </div>
              <div>
                <h2 className="text-2xl font-semibold tracking-tight text-white lg:text-3xl">
                  {portal.title}
                </h2>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-200 lg:text-base">
                  {portal.description || tr("catalogs.hero.no_description", "Browse this collection through a calmer discovery view designed for pilot sessions, lightweight consultation, and stakeholder conversations.")}
                </p>
              </div>
              <div className="flex flex-wrap gap-3 text-sm text-slate-200">
                {portal.source_label && (
                  <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                      {tr("catalogs.results.scope_source", "Collection origin")}
                    </p>
                    <p className="mt-1 font-medium text-white">{portal.source_label}</p>
                  </div>
                )}
                <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                    {tr("catalogs.results.scope_search", "Default query")}
                  </p>
                  <p className="mt-1 font-medium text-white">
                    {portal.search || tr("catalogs.results.scope_search_any", "Open discovery")}
                  </p>
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                  {tr("catalogs.hero.readiness_title", "Session mode")}
                </p>
                <p className="mt-2 text-base font-semibold text-white">
                  {portal.visibility === "public"
                    ? tr("catalogs.hero.public_hint", "Ready to share for read-only consultation")
                    : portal.visibility === "org"
                      ? tr("catalogs.hero.org_hint", "Visible to organization members with a lighter discovery experience")
                      : tr("catalogs.hero.private_hint", "Private collection under active setup")}
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                  {tr("catalogs.hero.discovery_title", "How to use it")}
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-200">
                  {tr("catalogs.hero.discovery_body", "Start with a broad search, refine with the facet panel, and open the record detail when you need the complete metadata story.")}
                </p>
              </div>
            </div>
          </div>
        </section>
      )}

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

      {portal?.source_label && (
        <section className="rounded-2xl border border-violet-200 bg-violet-50 px-5 py-4 text-sm text-violet-900 dark:border-violet-800 dark:bg-violet-950/30 dark:text-violet-100">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-violet-600 dark:text-violet-300">
            {tr("catalogs.source_context.eyebrow", "Collection origin")}
          </p>
          <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1">
            <span className="font-semibold">{portal.source_label}</span>
            {portal.source_context?.format && <span>{String(portal.source_context.format).toUpperCase()}</span>}
            {portal.source_context?.rows !== null && portal.source_context?.rows !== undefined && (
              <span>{String(portal.source_context.rows)} {tr("catalogs.source_context.rows", "rows")}</span>
            )}
          </div>
        </section>
      )}

      <section className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="space-y-4 rounded-2xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="rounded-2xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-950">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">
                  {tr("catalogs.manage.eyebrow", "Portal settings")}
                </p>
                <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-white">
                  {tr("catalogs.manage.title", "Adjust this collection")}
                </p>
              </div>
              {isAuthenticated ? (
                <button
                  onClick={() => setEditing((prev) => !prev)}
                  className="rounded-xl border border-gray-200 px-3 py-1.5 text-sm font-medium text-gray-700 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
                >
                  {editing ? tr("common.cancel", "Cancel") : tr("common.edit", "Edit")}
                </button>
              ) : (
                <span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                  {tr("catalogs.visibility.public_readonly", "Public read-only")}
                </span>
              )}
            </div>

            {!isAuthenticated && (
              <p className="mt-3 text-sm text-gray-600 dark:text-gray-300">
                {tr("catalogs.manage.readonly_help", "This public portal is open for consultation only. Sign in to manage filters, visibility, or descriptive settings.")}
              </p>
            )}

            {editing && isAuthenticated && (
              <div className="mt-4 space-y-3">
                <input
                  value={editForm.title}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, title: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                  placeholder={tr("catalogs.field.title", "Title")}
                />
                <textarea
                  rows={3}
                  value={editForm.description}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, description: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                  placeholder={tr("catalogs.field.description", "Description")}
                />
                <input
                  value={editForm.source_label}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, source_label: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                  placeholder={tr("catalogs.manage.source_label", "Collection origin label")}
                />
                <select
                  value={editForm.visibility}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, visibility: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                >
                  <option value="private">{tr("catalogs.visibility.private", "Private workspace")}</option>
                  <option value="org">{tr("catalogs.visibility.org", "Organization members")}</option>
                  <option value="public">{tr("catalogs.visibility.public", "Public read-only")}</option>
                </select>
                <input
                  value={editForm.search}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, search: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                  placeholder={tr("catalogs.manage.default_search", "Default search")}
                />
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={editForm.min_quality}
                  onChange={(event) => setEditForm((prev) => ({ ...prev, min_quality: event.target.value }))}
                  className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                  placeholder={tr("catalogs.field.min_quality", "Minimum quality")}
                />
                <button
                  onClick={savePortal}
                  disabled={saving}
                  className="w-full rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                >
                  {saving ? tr("catalogs.saving", "Saving...") : tr("catalogs.save", "Save portal")}
                </button>
              </div>
            )}
          </div>

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
              <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400 dark:text-gray-500">
                {tr("catalogs.results.section_eyebrow", "Catalog results")}
              </p>
              <h2 className="mt-1 text-lg font-semibold text-gray-900 dark:text-white">
                {tr("catalogs.results.section_title", "Browse the collection")}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {results
                  ? tr("catalogs.results_count", "{count} records in this portal").replace("{count}", results.total.toLocaleString())
                  : tr("catalogs.results_loading", "Loading records...")}
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                {portal?.domain_id || "—"}
              </span>
              <span className={`rounded-full px-3 py-1 text-xs font-medium ${visibilityTone(portal?.visibility)}`}>
                {visibilityLabel(portal?.visibility)}
              </span>
            </div>
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
                  className="block rounded-3xl border border-gray-200 p-5 transition hover:border-blue-300 hover:bg-blue-50/40 hover:shadow-sm dark:border-gray-800 dark:hover:border-blue-700 dark:hover:bg-blue-950/20"
                >
                  <div className="flex flex-wrap items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-2">
                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                          {record.entity_type || tr("catalogs.record.type_unknown", "Record")}
                        </span>
                        <span className="rounded-full bg-blue-100 px-2.5 py-1 text-[11px] font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                          {record.enrichment_status || tr("catalogs.record.status_unknown", "Unknown status")}
                        </span>
                      </div>
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
                      <div className="text-xs font-medium text-blue-600 dark:text-blue-400">
                        {tr("catalogs.record.open", "Open full record")} →
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
