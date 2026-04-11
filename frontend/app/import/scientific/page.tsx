"use client";
import { useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useLanguage } from "@/app/contexts/LanguageContext";

type Source = { id: string; name: string; requires_key: boolean };
type PreviewRecord = {
  title: string;
  doi: string | null;
  authors: string[];
  year: number | null;
  journal: string | null;
  concepts: string[];
  source_api: string;
};
type ImportResult = { imported: number; skipped: number };
type Step = "query" | "preview" | "done";

async function readJsonOrThrow<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null);
  if (!response.ok) {
    const detail =
      payload && typeof payload === "object" && "detail" in payload
        ? String(payload.detail)
        : "Request failed";
    throw new Error(detail);
  }
  return payload as T;
}

export default function ScientificImportPage() {
  const { t } = useLanguage();
  const [sources, setSources] = useState<Source[]>([]);
  const [sourcesLoaded, setSourcesLoaded] = useState(false);
  const [source, setSource] = useState("crossref");
  const [mode, setMode] = useState<"search" | "dois">("search");
  const [query, setQuery] = useState("");
  const [doiText, setDoiText] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [libraryId, setLibraryId] = useState("");
  const [maxResults, setMaxResults] = useState(20);
  const [step, setStep] = useState<Step>("query");
  const [preview, setPreview] = useState<PreviewRecord[]>([]);
  const [result, setResult] = useState<ImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSources = async () => {
    if (sourcesLoaded) return;
    try {
      const resp = await apiFetch("/scientific/sources");
      const data: Source[] = await resp.json();
      setSources(data);
      setSourcesLoaded(true);
    } catch {
      // fallback to hardcoded default in select
    }
  };

  const selectedSource = sources.find((s) => s.id === source);

  const buildConfig = (): Record<string, string> => {
    const cfg: Record<string, string> = {};
    if (apiKey) cfg.api_key = apiKey;
    if (libraryId) cfg.library_id = libraryId;
    return cfg;
  };

  const handlePreview = async () => {
    setLoading(true);
    setError(null);
    try {
      let data: PreviewRecord[];
      if (mode === "dois") {
        const dois = doiText.split(/[\n,]+/).map((d) => d.trim()).filter(Boolean);
        const resp = await apiFetch("/scientific/dois/preview", {
          method: "POST",
          body: JSON.stringify({ dois, source, config: buildConfig() }),
        });
        data = await readJsonOrThrow<PreviewRecord[]>(resp);
      } else {
        const resp = await apiFetch("/scientific/search", {
          method: "POST",
          body: JSON.stringify({ source, query, max_results: maxResults, config: buildConfig() }),
        });
        data = await readJsonOrThrow<PreviewRecord[]>(resp);
      }
      setPreview(data);
      setStep("preview");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("page.import.scientific.error.search"));
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    setLoading(true);
    setError(null);
    try {
      let data: ImportResult;
      if (mode === "dois") {
        const dois = doiText.split(/[\n,]+/).map((d) => d.trim()).filter(Boolean);
        const resp = await apiFetch("/scientific/dois", {
          method: "POST",
          body: JSON.stringify({ dois, source, config: buildConfig() }),
        });
        data = await readJsonOrThrow<ImportResult>(resp);
      } else {
        const resp = await apiFetch("/scientific/import", {
          method: "POST",
          body: JSON.stringify({ source, query, max_results: maxResults, config: buildConfig() }),
        });
        data = await readJsonOrThrow<ImportResult>(resp);
      }
      setResult(data);
      setStep("done");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : t("page.import.scientific.error.import"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto py-8 px-4 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t("page.import.scientific.title")}</h1>
        <p className="text-sm text-gray-500 mt-1">
          {t("page.import.scientific.description")}
        </p>
      </div>

      {/* Progress steps */}
      <div className="flex gap-2 text-xs font-medium">
        {(["query", "preview", "done"] as Step[]).map((s, i) => (
          <span
            key={s}
            className={`px-3 py-1 rounded-full ${
              step === s
                ? "bg-indigo-600 text-white"
                : "bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400"
            }`}
          >
            {i + 1}. {t(`page.import.scientific.step.${s}`)}
          </span>
        ))}
      </div>

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {error}
        </div>
      )}

      {/* Step 1: Query */}
      {step === "query" && (
        <div
          className="space-y-4 rounded-xl border border-gray-200 dark:border-gray-700 p-5 bg-white dark:bg-gray-900"
          onClick={loadSources}
        >
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{t("page.import.scientific.source")}</label>
              <select
                value={source}
                onChange={(e) => setSource(e.target.value)}
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
              >
                {sources.length === 0 && <option value="crossref">CrossRef</option>}
                {sources.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name}
                    {s.requires_key ? " 🔑" : ""}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{t("page.import.scientific.mode")}</label>
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value as "search" | "dois")}
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
              >
                <option value="search">{t("page.import.scientific.mode.search")}</option>
                <option value="dois">{t("page.import.scientific.mode.dois")}</option>
              </select>
            </div>
          </div>

          {selectedSource?.requires_key && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{t("page.import.scientific.api_key")}</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Your API key"
                  className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
                />
              </div>
              {source === "zotero" && (
                <div>
                  <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                    {t("page.import.scientific.library_id")}
                  </label>
                  <input
                    type="text"
                    value={libraryId}
                    onChange={(e) => setLibraryId(e.target.value)}
                    placeholder={t("page.import.scientific.library_id_placeholder")}
                    className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
                  />
                </div>
              )}
            </div>
          )}

          {mode === "search" ? (
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                {source === "orcid" ? t("page.import.scientific.orcid_label") : t("page.import.scientific.search_label")}
              </label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={source === "orcid" ? t("page.import.scientific.orcid_placeholder") : t("page.import.scientific.search_placeholder")}
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
              />
              <div className="mt-2 flex items-center gap-2 text-xs text-gray-500">
                <span>{t("page.import.scientific.max_results")}</span>
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={maxResults}
                  onChange={(e) => setMaxResults(Number(e.target.value))}
                  className="w-16 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-2 py-1 text-xs"
                />
              </div>
            </div>
          ) : (
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
                {t("page.import.scientific.dois_label")}
              </label>
              <textarea
                value={doiText}
                onChange={(e) => setDoiText(e.target.value)}
                rows={6}
                placeholder={"10.1038/nature12373\n10.1016/j.cell.2022.01.001"}
                className="w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2 font-mono"
              />
            </div>
          )}

          <button
            onClick={handlePreview}
            disabled={loading || (mode === "search" && !query) || (mode === "dois" && !doiText)}
            className="w-full rounded-md bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium py-2 px-4 transition-colors"
          >
            {loading ? t("page.import.scientific.preview_loading") : t("page.import.scientific.preview_cta")}
          </button>
        </div>
      )}

      {/* Step 2: Preview */}
      {step === "preview" && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600 dark:text-gray-400">{t("page.import.scientific.results_found", { count: preview.length })}</span>
            <button onClick={() => setStep("query")} className="text-xs text-indigo-600 hover:underline">
              {t("page.import.scientific.change_query")}
            </button>
          </div>
          <div className="overflow-auto rounded-xl border border-gray-200 dark:border-gray-700">
            <table className="min-w-full text-xs">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  {[
                    t("page.import.scientific.table.title"),
                    t("page.import.scientific.table.authors"),
                    t("page.import.scientific.table.year"),
                    t("page.import.scientific.table.doi"),
                    t("page.import.scientific.table.source"),
                  ].map((h) => (
                    <th key={h} className="px-3 py-2 text-left font-medium text-gray-600 dark:text-gray-400">
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                {preview.map((r, i) => (
                  <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                    <td className="px-3 py-2 max-w-xs truncate" title={r.title}>
                      {r.title}
                    </td>
                    <td className="px-3 py-2 text-gray-500">
                      {(r.authors || []).slice(0, 2).join("; ")}
                      {(r.authors?.length ?? 0) > 2 ? " …" : ""}
                    </td>
                    <td className="px-3 py-2 text-gray-500">{r.year ?? "—"}</td>
                    <td className="px-3 py-2 font-mono text-gray-500 max-w-[160px] truncate">{r.doi ?? "—"}</td>
                    <td className="px-3 py-2">
                      <span className="rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 px-2 py-0.5">
                        {r.source_api}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button
            onClick={handleImport}
            disabled={loading}
            className="w-full rounded-md bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white text-sm font-medium py-2 px-4 transition-colors"
          >
            {loading ? t("page.import.scientific.import_loading") : t("page.import.scientific.import_cta", { count: preview.length })}
          </button>
        </div>
      )}

      {/* Step 3: Done */}
      {step === "done" && result && (
        <div className="rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-6 text-center space-y-3">
          <div className="text-3xl font-bold text-green-700 dark:text-green-400">{result.imported}</div>
          <div className="text-sm text-green-700 dark:text-green-300">{t("page.import.scientific.success")}</div>
          {result.skipped > 0 && (
            <div className="text-xs text-gray-500">{t("page.import.scientific.skipped", { count: result.skipped })}</div>
          )}
          <div className="flex gap-3 justify-center pt-2">
            <Link href="/" className="rounded-md bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2">
              {t("page.import.scientific.view_entities")}
            </Link>
            <button
              onClick={() => {
                setStep("query");
                setPreview([]);
                setResult(null);
              }}
              className="rounded-md border border-gray-300 dark:border-gray-600 text-sm px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              {t("page.import.scientific.new_import")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
