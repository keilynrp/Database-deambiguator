"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "../../contexts/LanguageContext";
import { PageHeader, StatCard } from "../../components/ui";

// ── Export helpers ────────────────────────────────────────────────────────────

type ExportFormat = "graphml" | "cytoscape" | "jsonld";

const EXPORT_FORMATS: { value: ExportFormat; label: string; ext: string; desc: string; color: string }[] = [
  {
    value: "graphml",
    label: "GraphML",
    ext: "graphml",
    desc: "Gephi · yEd · igraph",
    color: "bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100 dark:bg-emerald-500/10 dark:border-emerald-500/30 dark:text-emerald-400",
  },
  {
    value: "cytoscape",
    label: "Cytoscape JSON",
    ext: "json",
    desc: "Cytoscape.js · Cytoscape Desktop",
    color: "bg-indigo-50 border-indigo-200 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-500/10 dark:border-indigo-500/30 dark:text-indigo-400",
  },
  {
    value: "jsonld",
    label: "JSON-LD",
    ext: "jsonld",
    desc: "Semantic web · Linked Data",
    color: "bg-violet-50 border-violet-200 text-violet-700 hover:bg-violet-100 dark:bg-violet-500/10 dark:border-violet-500/30 dark:text-violet-400",
  },
];

async function downloadGraph(format: ExportFormat, domain: string) {
  const params = new URLSearchParams({ format });
  if (domain.trim()) params.set("domain", domain.trim());
  const res = await apiFetch(`/export/graph?${params.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Export failed" }));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  const blob = await res.blob();
  const fmt = EXPORT_FORMATS.find((f) => f.value === format)!;
  const domainSlug = domain.trim() ? `_${domain.trim()}` : "";
  const filename = `ukip_graph${domainSlug}.${fmt.ext}`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

interface GraphStats {
  total_nodes: number;
  total_edges: number;
  total_components: number;
  largest_component_size: number;
  top_pagerank: Array<{ entity_id: number; primary_label: string | null; score: number }>;
  top_degree:   Array<{ entity_id: number; primary_label: string | null; total_degree: number }>;
}

interface PathResult {
  found: boolean;
  length?: number;
  relations?: string[];
  steps?: Array<{ entity_id: number; primary_label: string | null }>;
}

interface CommunitySummary {
  community_id: number;
  size: number;
  internal_edges: number;
  density: number;
  entity_ids: number[];
  top_relations: Array<{ relation_type: string; count: number }>;
  leader: {
    entity_id: number;
    primary_label: string | null;
    total_degree: number;
  };
}

interface CommunityResponse {
  total_communities: number;
  communities: CommunitySummary[];
}

export default function GraphAnalyticsPage() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<GraphStats | null>(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [errorStats, setErrorStats] = useState<string | null>(null);

  // Path finder state
  const [fromId, setFromId] = useState("");
  const [toId, setToId] = useState("");
  const [pathResult, setPathResult] = useState<PathResult | null>(null);
  const [loadingPath, setLoadingPath] = useState(false);
  const [pathError, setPathError] = useState<string | null>(null);
  const [communities, setCommunities] = useState<CommunityResponse | null>(null);
  const [loadingCommunities, setLoadingCommunities] = useState(true);
  const [communityError, setCommunityError] = useState<string | null>(null);

  // Export state
  const [exportDomain, setExportDomain] = useState("");
  const [exportingFormat, setExportingFormat] = useState<ExportFormat | null>(null);
  const [exportError, setExportError] = useState<string | null>(null);

  useEffect(() => {
    setLoadingStats(true);
    apiFetch("/graph/stats")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => setStats(data))
      .catch((e) => setErrorStats(`${t("page.graph.error_load_stats")} (${e})`))
      .finally(() => setLoadingStats(false));
  }, [t]);

  useEffect(() => {
    setLoadingCommunities(true);
    apiFetch("/graph/communities?limit=8")
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => setCommunities(data))
      .catch((e) => setCommunityError(`${t("page.graph.error_load_communities")} (${e})`))
      .finally(() => setLoadingCommunities(false));
  }, [t]);

  async function handleExport(format: ExportFormat) {
    setExportingFormat(format);
    setExportError(null);
    try {
      await downloadGraph(format, exportDomain);
    } catch (e: unknown) {
      setExportError(e instanceof Error ? e.message : t("page.graph.export_failed"));
    } finally {
      setExportingFormat(null);
    }
  }

  async function findPath() {
    if (!fromId || !toId) return;
    setLoadingPath(true);
    setPathResult(null);
    setPathError(null);
    try {
      const r = await apiFetch(`/graph/path?from_id=${fromId}&to_id=${toId}`);
      if (r.ok) {
        setPathResult(await r.json());
      } else {
        const body = await r.json().catch(() => ({}));
        setPathError(body.detail ?? `Error ${r.status}`);
      }
    } catch {
      setPathError(t("page.graph.network_error"));
    } finally {
      setLoadingPath(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <PageHeader
          title={t("page.graph.title")}
          description={t("page.graph.description")}
        />

        {/* Stats cards */}
        {loadingStats ? (
          <div className="flex h-32 items-center justify-center">
            <svg className="h-6 w-6 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : errorStats ? (
          <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
            {errorStats}
          </div>
        ) : stats ? (
          <>
            <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <StatCard
                label={t("page.graph.total_nodes")}
                value={stats.total_nodes.toLocaleString()}
                icon={
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M12 18a6 6 0 100-12 6 6 0 000 12z" />
                  </svg>
                }
              />
              <StatCard
                label={t("page.graph.total_edges")}
                value={stats.total_edges.toLocaleString()}
                icon={
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M5 12h14" />
                  </svg>
                }
              />
              <StatCard
                label={t("page.graph.components")}
                value={stats.total_components.toLocaleString()}
                icon={
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M3.75 6A2.25 2.25 0 016 3.75h2.25A2.25 2.25 0 0110.5 6v2.25a2.25 2.25 0 01-2.25 2.25H6a2.25 2.25 0 01-2.25-2.25V6z" />
                  </svg>
                }
              />
              <StatCard
                label={t("page.graph.largest_component")}
                value={stats.largest_component_size.toLocaleString()}
                icon={
                  <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M13.5 16.875h3.375m0 0h3.375m-3.375 0V13.5m0 3.375v3.375M6 10.5h2.25a2.25 2.25 0 002.25-2.25V6a2.25 2.25 0 00-2.25-2.25H6A2.25 2.25 0 003.75 6v2.25A2.25 2.25 0 006 10.5z" />
                  </svg>
                }
              />
            </div>

            {stats.total_nodes === 0 ? (
              <div className="mt-8 rounded-xl border border-gray-200 bg-white p-12 text-center dark:border-gray-800 dark:bg-gray-900">
                <svg className="mx-auto mb-3 h-10 w-10 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M13.5 16.875h3.375m0 0h3.375m-3.375 0V13.5m0 3.375v3.375M6 10.5h2.25a2.25 2.25 0 002.25-2.25V6a2.25 2.25 0 00-2.25-2.25H6A2.25 2.25 0 003.75 6v2.25A2.25 2.25 0 006 10.5zm0 9.75h2.25A2.25 2.25 0 0010.5 18v-2.25a2.25 2.25 0 00-2.25-2.25H6a2.25 2.25 0 00-2.25 2.25V18A2.25 2.25 0 006 20.25zm9.75-9.75H18a2.25 2.25 0 002.25-2.25V6A2.25 2.25 0 0018 3.75h-2.25A2.25 2.25 0 0013.5 6v2.25a2.25 2.25 0 002.25 2.25z" />
                </svg>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{t("page.graph.no_relationships")}</p>
                <p className="mt-1 text-xs text-gray-400 dark:text-gray-500">
                  {t("page.graph.add_relationships_hint")}
                </p>
              </div>
            ) : (
              <>
              <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Top by PageRank */}
                <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                  <h2 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">
                    {t("page.graph.top_by_pagerank")}
                  </h2>
                  {stats.top_pagerank.length === 0 ? (
                    <p className="text-xs text-gray-400">{t("common.no_data")}</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-100 dark:border-gray-800">
                          <th className="pb-2 text-left text-xs font-medium text-gray-400">#</th>
                          <th className="pb-2 text-left text-xs font-medium text-gray-400">{t("page.graph.entity")}</th>
                          <th className="pb-2 text-right text-xs font-medium text-gray-400">{t("page.graph.score")}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
                        {stats.top_pagerank.map((row, idx) => (
                          <tr key={row.entity_id}>
                            <td className="py-2 text-xs text-gray-400">{idx + 1}</td>
                            <td className="py-2">
                              <Link
                                href={`/entities/${row.entity_id}`}
                                className="text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                              >
                                {row.primary_label ?? `#${row.entity_id}`}
                              </Link>
                            </td>
                            <td className="py-2 text-right text-xs tabular-nums text-gray-700 dark:text-gray-300">
                              {row.score.toFixed(4)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>

                {/* Top by Degree */}
                <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                  <h2 className="mb-4 text-sm font-semibold text-gray-900 dark:text-white">
                    {t("page.graph.top_by_degree")}
                  </h2>
                  {stats.top_degree.length === 0 ? (
                    <p className="text-xs text-gray-400">{t("common.no_data")}</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-100 dark:border-gray-800">
                          <th className="pb-2 text-left text-xs font-medium text-gray-400">#</th>
                          <th className="pb-2 text-left text-xs font-medium text-gray-400">{t("page.graph.entity")}</th>
                          <th className="pb-2 text-right text-xs font-medium text-gray-400">{t("page.graph.degree")}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-50 dark:divide-gray-800/50">
                        {stats.top_degree.map((row, idx) => (
                          <tr key={row.entity_id}>
                            <td className="py-2 text-xs text-gray-400">{idx + 1}</td>
                            <td className="py-2">
                              <Link
                                href={`/entities/${row.entity_id}`}
                                className="text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                              >
                                {row.primary_label ?? `#${row.entity_id}`}
                              </Link>
                            </td>
                            <td className="py-2 text-right text-xs tabular-nums text-gray-700 dark:text-gray-300">
                              {row.total_degree}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </div>

              <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-sm font-semibold text-gray-900 dark:text-white">
                      {t("page.graph.research_communities")}
                    </h2>
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      {t("page.graph.research_communities_description")}
                    </p>
                  </div>
                  {communities && (
                    <span className="rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-300">
                      {communities.total_communities} {t("page.graph.detected")}
                    </span>
                  )}
                </div>

                {loadingCommunities ? (
                  <div className="flex h-20 items-center justify-center">
                    <svg className="h-5 w-5 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  </div>
                ) : communityError ? (
                  <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
                    {communityError}
                  </div>
                ) : communities && communities.communities.length > 0 ? (
                  <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
                    {communities.communities.map((community) => (
                      <div key={community.community_id} className="rounded-2xl border border-gray-200 bg-gray-50 p-5 dark:border-gray-800 dark:bg-gray-950/60">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-gray-500 dark:text-gray-400">
                              {t("page.graph.community")} {community.community_id + 1}
                            </p>
                            <p className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
                              {t("page.graph.leader")}: {community.leader.primary_label ?? `Entity #${community.leader.entity_id}`}
                            </p>
                          </div>
                          <span className="rounded-full bg-indigo-100 px-2.5 py-1 text-xs font-semibold text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300">
                            {community.size} {t("page.graph.nodes")}
                          </span>
                        </div>
                        <div className="mt-4 grid grid-cols-3 gap-3 text-center">
                          <div className="rounded-xl bg-white p-3 dark:bg-gray-900">
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t("page.graph.density")}</p>
                            <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{community.density}</p>
                          </div>
                          <div className="rounded-xl bg-white p-3 dark:bg-gray-900">
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t("page.graph.edges")}</p>
                            <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{community.internal_edges}</p>
                          </div>
                          <div className="rounded-xl bg-white p-3 dark:bg-gray-900">
                            <p className="text-xs text-gray-500 dark:text-gray-400">{t("page.graph.leader_degree")}</p>
                            <p className="mt-1 text-sm font-semibold text-gray-900 dark:text-white">{community.leader.total_degree}</p>
                          </div>
                        </div>
                        {community.top_relations.length > 0 && (
                          <div className="mt-4 flex flex-wrap gap-2">
                            {community.top_relations.map((relation) => (
                              <span
                                key={`${community.community_id}-${relation.relation_type}`}
                                className="rounded-full bg-white px-3 py-1 text-xs font-medium text-gray-700 dark:bg-gray-900 dark:text-gray-300"
                              >
                                {relation.relation_type} · {relation.count}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {t("page.graph.no_communities")}
                  </p>
                )}
              </div>
              </>
            )}
          </>
        ) : null}

        {/* Path Finder */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">{t("page.graph.path_finder")}</h2>
          <p className="mb-4 text-xs text-gray-500 dark:text-gray-400">
            {t("page.graph.path_finder_description")}
          </p>
          <div className="flex flex-wrap items-end gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                {t("page.graph.from_entity_id")}
              </label>
              <input
                type="number"
                min={1}
                value={fromId}
                onChange={(e) => setFromId(e.target.value)}
                className="w-36 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                placeholder={t("page.graph.entity_id_example_1")}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
                {t("page.graph.to_entity_id")}
              </label>
              <input
                type="number"
                min={1}
                value={toId}
                onChange={(e) => setToId(e.target.value)}
                className="w-36 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
                placeholder={t("page.graph.entity_id_example_5")}
              />
            </div>
            <button
              onClick={findPath}
              disabled={loadingPath || !fromId || !toId}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loadingPath ? t("page.graph.searching") : t("page.graph.find_path")}
            </button>
          </div>

          {pathError && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-xs text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-400">
              {pathError}
            </div>
          )}

          {pathResult && (
            <div className="mt-4">
              {!pathResult.found ? (
                <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-700 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-400">
                  <svg className="h-4 w-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                      d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                  </svg>
                  {t("page.graph.no_directed_path")} {fromId} {t("page.graph.to_entity")} {toId}.
                </div>
              ) : (
                <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-900/10">
                  <div className="mb-3 flex items-center gap-3 text-xs">
                    <span className="font-semibold text-emerald-700 dark:text-emerald-400">
                      {t("page.graph.path_found")}
                    </span>
                    <span className="text-emerald-600 dark:text-emerald-500">
                      {t("page.graph.length")}: {pathResult.length} {pathResult.length !== 1 ? t("page.graph.hops") : t("page.graph.hop")}
                    </span>
                    {pathResult.relations && pathResult.relations.length > 0 && (
                      <span className="text-emerald-600 dark:text-emerald-500">
                        {t("page.graph.via")}: {pathResult.relations.join(" → ")}
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-1">
                    {pathResult.steps?.map((step, idx) => (
                      <span key={step.entity_id} className="flex items-center gap-1">
                        <Link
                          href={`/entities/${step.entity_id}`}
                          className="rounded-md bg-white px-2 py-1 text-xs font-medium text-indigo-700 shadow-sm ring-1 ring-indigo-200 hover:ring-indigo-400 dark:bg-gray-800 dark:text-indigo-300 dark:ring-indigo-800"
                        >
                          {step.primary_label ?? `#${step.entity_id}`}
                        </Link>
                        {idx < (pathResult.steps?.length ?? 0) - 1 && (
                          <span className="flex items-center gap-1 text-xs text-gray-400 dark:text-gray-500">
                            <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                            <span className="text-[10px] text-indigo-500 dark:text-indigo-400">
                              {pathResult.relations?.[idx]}
                            </span>
                            <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                          </span>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Export Graph */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
          <h2 className="mb-1 text-sm font-semibold text-gray-900 dark:text-white">{t("page.graph.export_graph")}</h2>
          <p className="mb-4 text-xs text-gray-500 dark:text-gray-400">
            {t("page.graph.export_graph_description")}
          </p>

          {/* Domain filter */}
          <div className="mb-4">
            <label className="mb-1 block text-xs font-medium text-gray-600 dark:text-gray-400">
              {t("page.graph.domain_filter")} <span className="font-normal text-gray-400">({t("page.graph.leave_blank_all_domains")})</span>
            </label>
            <input
              type="text"
              value={exportDomain}
              onChange={(e) => setExportDomain(e.target.value)}
              placeholder={t("page.graph.domain_example")}
              className="w-56 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm text-gray-900 placeholder-gray-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 dark:border-gray-700 dark:bg-gray-800 dark:text-white"
            />
          </div>

          {/* Format buttons */}
          <div className="flex flex-wrap gap-3">
            {EXPORT_FORMATS.map((fmt) => {
              const isLoading = exportingFormat === fmt.value;
              return (
                <button
                  key={fmt.value}
                  onClick={() => handleExport(fmt.value)}
                  disabled={exportingFormat !== null}
                  className={`flex items-center gap-2 rounded-xl border px-4 py-3 text-left transition-colors disabled:opacity-60 ${fmt.color}`}
                >
                  {isLoading ? (
                    <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                  ) : (
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                    </svg>
                  )}
                  <div>
                    <p className="text-xs font-semibold">{isLoading ? t("page.graph.exporting") : fmt.label}</p>
                    <p className="text-[10px] opacity-70">{fmt.desc}</p>
                  </div>
                </button>
              );
            })}
          </div>

          {exportError && (
            <div className="mt-3 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 dark:border-red-800 dark:bg-red-900/20">
              <svg className="h-4 w-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p className="text-xs text-red-700 dark:text-red-400">{exportError}</p>
              <button onClick={() => setExportError(null)} className="ml-auto text-red-400 hover:text-red-600">
                <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
