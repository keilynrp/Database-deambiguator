"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { PageHeader, EmptyState, ErrorBanner, useToast } from "../components/ui";
import { useDomain } from "../contexts/DomainContext";
import { useLanguage } from "../contexts/LanguageContext";

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
  created_at: string | null;
}

const DEFAULT_FACETS = ["entity_type", "validation_status", "enrichment_status", "source"];

export default function CatalogPortalsPage() {
  const { domains, activeDomainId } = useDomain();
  const { t } = useLanguage();
  const { toast } = useToast();
  const router = useRouter();
  const searchParams = useSearchParams();
  const tr = (key: string, fallback: string) => {
    const value = t(key);
    return value === key ? fallback : value;
  };

  const [portals, setPortals] = useState<CatalogPortal[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: searchParams.get("title") ?? "",
    slug: searchParams.get("slug") ?? "",
    description: searchParams.get("description") ?? "",
    domain_id: activeDomainId || "default",
    visibility: searchParams.get("visibility") ?? "private",
    source_label: searchParams.get("source_label") ?? "",
    search: searchParams.get("search") ?? "",
    min_quality: searchParams.get("min_quality") ?? "",
    ft_entity_type: searchParams.get("ft_entity_type") ?? "",
    ft_validation_status: searchParams.get("ft_validation_status") ?? "",
    ft_enrichment_status: searchParams.get("ft_enrichment_status") ?? "",
    ft_source: searchParams.get("ft_source") ?? "",
    default_sort: searchParams.get("default_sort") ?? "primary_label",
    default_order: searchParams.get("default_order") ?? "asc",
  });

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      domain_id: searchParams.get("domain_id") || prev.domain_id || activeDomainId || "default",
    }));
  }, [activeDomainId, searchParams]);

  const loadPortals = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiFetch("/catalogs");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setPortals(await res.json());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : tr("catalogs.load_failed", "Failed to load catalog portals."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadPortals();
  }, []);

  const domainOptions = useMemo(
    () => domains.map((domain) => ({ id: domain.id, name: domain.name })),
    [domains],
  );

  const handleCreate = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const payload = {
        ...form,
        min_quality: form.min_quality ? Number(form.min_quality) : null,
        source_context: {
          format: searchParams.get("source_format") ?? null,
          rows: searchParams.get("source_rows") ? Number(searchParams.get("source_rows")) : null,
          seeded_from: searchParams.get("seeded_from") ?? null,
        },
        featured_facets: DEFAULT_FACETS,
      };
      const res = await apiFetch("/catalogs", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => null);
        throw new Error(detail?.detail || `HTTP ${res.status}`);
      }
      const created = await res.json();
      toast(
        `${tr("catalogs.created_title", "Catalog portal created")}: ${tr("catalogs.created_description", "The portal is ready to browse and share internally.")}`,
        "success",
      );
      await loadPortals();
      router.push(`/catalogs/${created.slug}`);
    } catch (saveError) {
      const message = saveError instanceof Error ? saveError.message : tr("catalogs.create_failed", "Failed to create catalog portal.");
      setError(message);
      toast(`${tr("catalogs.create_failed_title", "Unable to create portal")}: ${message}`, "error");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: tr("nav.home", "Knowledge Explorer"), href: "/" },
          { label: tr("nav.catalogs", "Catalog Portals") },
        ]}
        title={tr("catalogs.title", "Catalog Portals")}
        description={tr("catalogs.subtitle", "Turn a scoped set of records into a friendlier discovery portal for pilot sessions and internal access.")}
      />

      {error && <ErrorBanner message={error} />}

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <form
          onSubmit={handleCreate}
          className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900"
        >
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-600 dark:text-blue-400">
              {tr("catalogs.create_eyebrow", "New portal")}
            </p>
            <h2 className="mt-2 text-xl font-semibold text-gray-900 dark:text-white">
              {tr("catalogs.create_title", "Publish a scoped catalog view")}
            </h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
              {tr("catalogs.create_help", "Start with one domain and a few saved filters. We will keep this first cut private to your workspace.")}
            </p>
            {form.source_label && (
              <div className="mt-4 rounded-2xl border border-violet-200 bg-violet-50 px-4 py-3 text-sm text-violet-800 dark:border-violet-800 dark:bg-violet-950/30 dark:text-violet-200">
                <p className="font-semibold">{tr("catalogs.source_seeded", "Seeded from import")}</p>
                <p className="mt-1">{form.source_label}</p>
              </div>
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.title", "Title")}</span>
              <input
                required
                value={form.title}
                onChange={(event) => setForm((prev) => ({ ...prev, title: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder={tr("catalogs.field.title_placeholder", "Research portfolio catalog")}
              />
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.slug", "Slug")}</span>
              <input
                required
                value={form.slug}
                onChange={(event) => setForm((prev) => ({ ...prev, slug: event.target.value.toLowerCase().replace(/\s+/g, "-") }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder="udg-science-portal"
              />
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300 md:col-span-2">
              <span>{tr("catalogs.field.description", "Description")}</span>
              <textarea
                rows={3}
                value={form.description}
                onChange={(event) => setForm((prev) => ({ ...prev, description: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder={tr("catalogs.field.description_placeholder", "A focused catalog for stakeholders who need broad discovery instead of the operational datatable.")}
              />
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.domain", "Domain")}</span>
              <select
                value={form.domain_id}
                onChange={(event) => setForm((prev) => ({ ...prev, domain_id: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
              >
                {domainOptions.map((domain) => (
                  <option key={domain.id} value={domain.id}>
                    {domain.name}
                  </option>
                ))}
              </select>
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.visibility", "Visibility")}</span>
              <select
                value={form.visibility}
                onChange={(event) => setForm((prev) => ({ ...prev, visibility: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
              >
                <option value="private">{tr("catalogs.visibility.private", "Private workspace")}</option>
                <option value="org">{tr("catalogs.visibility.org", "Organization members")}</option>
              </select>
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.entity_type", "Entity type filter")}</span>
              <input
                value={form.ft_entity_type}
                onChange={(event) => setForm((prev) => ({ ...prev, ft_entity_type: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder={tr("catalogs.field.entity_type_placeholder", "publication")}
              />
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
              <span>{tr("catalogs.field.min_quality", "Minimum quality")}</span>
              <input
                type="number"
                min="0"
                max="1"
                step="0.1"
                value={form.min_quality}
                onChange={(event) => setForm((prev) => ({ ...prev, min_quality: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder="0.6"
              />
            </label>
            <label className="space-y-2 text-sm text-gray-700 dark:text-gray-300 md:col-span-2">
              <span>{tr("catalogs.field.search", "Default search hint")}</span>
              <input
                value={form.search}
                onChange={(event) => setForm((prev) => ({ ...prev, search: event.target.value }))}
                className="w-full rounded-xl border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 dark:border-gray-700 dark:bg-gray-950 dark:text-white dark:focus:ring-blue-900/40"
                placeholder={tr("catalogs.field.search_placeholder", "CRISPR, education, materials science...")}
              />
            </label>
          </div>

          <div className="mt-6 flex items-center justify-between rounded-2xl bg-gray-50 px-4 py-3 text-sm text-gray-600 dark:bg-gray-950 dark:text-gray-300">
            <p>{tr("catalogs.create_note", "This first version stays private and uses the active domain plus saved filters as the collection scope.")}</p>
            <button
              type="submit"
              disabled={saving}
              className="rounded-xl bg-blue-600 px-4 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
            >
              {saving ? tr("catalogs.creating", "Creating...") : tr("catalogs.create_submit", "Create portal")}
            </button>
          </div>
        </form>

        <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
          <div className="mb-6">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-violet-600 dark:text-violet-400">
              {tr("catalogs.list_eyebrow", "Existing portals")}
            </p>
            <h2 className="mt-2 text-xl font-semibold text-gray-900 dark:text-white">
              {tr("catalogs.list_title", "Discovery spaces already available")}
            </h2>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
              {tr("catalogs.list_help", "Use these portals during demos and stakeholder sessions when the datatable feels too operational.")}
            </p>
          </div>

          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="h-24 animate-pulse rounded-2xl bg-gray-100 dark:bg-gray-800" />
              ))}
            </div>
          ) : portals.length === 0 ? (
            <EmptyState
              icon="document"
              color="violet"
              size="compact"
              title={tr("catalogs.empty_title", "No catalog portals yet")}
              description={tr("catalogs.empty_description", "Create the first portal on the left to turn your current workspace into a friendlier discovery view.")}
            />
          ) : (
            <div className="space-y-3">
              {portals.map((portal) => (
                <Link
                  key={portal.id}
                  href={`/catalogs/${portal.slug}`}
                  className="block rounded-2xl border border-gray-200 p-4 transition hover:border-blue-300 hover:bg-blue-50/50 dark:border-gray-800 dark:hover:border-blue-700 dark:hover:bg-blue-950/20"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2">
                        <h3 className="text-base font-semibold text-gray-900 dark:text-white">{portal.title}</h3>
                        <span className="rounded-full bg-gray-100 px-2.5 py-1 text-xs font-medium text-gray-600 dark:bg-gray-800 dark:text-gray-300">
                          {portal.domain_id}
                        </span>
                        <span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-medium text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                          {portal.visibility}
                        </span>
                      </div>
                      {portal.source_label && (
                        <p className="text-xs font-medium text-violet-700 dark:text-violet-300">
                          {portal.source_label}
                        </p>
                      )}
                      <p className="text-sm text-gray-600 dark:text-gray-300">
                        {portal.description || tr("catalogs.no_description", "No description yet.")}
                      </p>
                    </div>
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                      {tr("catalogs.open", "Open")} →
                    </span>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </section>
    </div>
  );
}
