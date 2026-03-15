"use client";

import { useState, useRef, useEffect } from "react";
import { apiFetch } from "@/lib/api";
import { PageHeader, useToast } from "../components/ui";
import { useDomain } from "../contexts/DomainContext";

// ── Function catalogue ────────────────────────────────────────────────────────

const FUNCTIONS = [
  { expr: "value.trim()",             label: "trim()",             desc: "Elimina espacios al inicio y fin" },
  { expr: "value.upper()",            label: "upper()",            desc: "Convierte a MAYÚSCULAS" },
  { expr: "value.lower()",            label: "lower()",            desc: "Convierte a minúsculas" },
  { expr: "value.title()",            label: "title()",            desc: "Primera letra de cada palabra en Mayúscula" },
  { expr: 'value.replace("old","new")', label: 'replace("old","new")', desc: "Reemplaza subcadena literal" },
  { expr: 'value.prefix("Dr. ")',     label: 'prefix("...")',      desc: "Añade prefijo si no existe" },
  { expr: 'value.suffix(" PhD")',     label: 'suffix("...")',      desc: "Añade sufijo si no existe" },
  { expr: "value.strip_html()",       label: "strip_html()",       desc: "Elimina etiquetas HTML" },
  { expr: "value.to_number()",        label: "to_number()",        desc: "Extrae valor numérico" },
  { expr: "value.slice(0,10)",        label: "slice(start,end)",   desc: "Subcadena por posición" },
  { expr: 'value.split(",")[0]',      label: 'split(",")[0]',      desc: "Primer token por delimitador" },
  { expr: 'value.strip(".")',         label: 'strip("chars")',     desc: "Elimina caracteres específicos" },
];

const FIELDS = [
  "primary_label", "secondary_label", "canonical_id",
  "entity_type", "domain", "validation_status",
  "enrichment_source", "enrichment_concepts",
];

interface PreviewRow {
  original: string | null;
  transformed: string | null;
  error: string | null;
}

// ── Diff highlight ─────────────────────────────────────────────────────────────

function DiffCell({ original, transformed }: { original: string | null; transformed: string | null }) {
  const orig = original ?? "";
  const trans = transformed ?? "";
  const changed = orig !== trans;
  return (
    <span className={changed ? "font-medium text-emerald-700 dark:text-emerald-400" : "text-gray-500 dark:text-gray-400"}>
      {trans || <span className="italic text-gray-300 dark:text-gray-600">vacío</span>}
    </span>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function TransformationsPage() {
  const { activeDomainId } = useDomain();
  const { toast } = useToast();

  const [field, setField] = useState(FIELDS[0]);
  const [expression, setExpression] = useState("value.trim()");
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [preview, setPreview] = useState<PreviewRow[]>([]);
  const [previewLoading, setPrevLoading] = useState(false);
  const [applying, setApplying] = useState(false);
  const [lastResult, setLastResult] = useState<{ affected: number; total: number } | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [history, setHistory] = useState<{ id: number; params: Record<string, string>; affected_count: number; reverted: boolean; created_at: string }[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredFns = FUNCTIONS.filter(
    (f) => !expression || f.expr.toLowerCase().includes(expression.toLowerCase().replace(/^value\./, ""))
  );

  async function runPreview() {
    setPrevLoading(true);
    setPreview([]);
    try {
      const res = await apiFetch("/transformations/preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ field, expression, domain_id: activeDomainId || null }),
      });
      if (!res.ok) {
        const err = await res.json();
        toast(err.detail || "Error en expresión", "error");
        return;
      }
      const data = await res.json();
      const rows: PreviewRow[] = data.original.map((orig: string | null, i: number) => ({
        original: orig,
        transformed: data.transformed[i],
        error: data.errors[i],
      }));
      setPreview(rows);
    } catch {
      toast("Error al conectar con el servidor", "error");
    } finally {
      setPrevLoading(false);
    }
  }

  async function runApply() {
    setConfirmOpen(false);
    setApplying(true);
    try {
      const res = await apiFetch("/transformations/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ field, expression, domain_id: activeDomainId || null }),
      });
      if (!res.ok) {
        const err = await res.json();
        toast(err.detail || "Error al aplicar", "error");
        return;
      }
      const data = await res.json();
      setLastResult({ affected: data.affected, total: data.total_scanned });
      toast(`Transformación aplicada: ${data.affected} filas modificadas`, "success");
      fetchHistory();
      runPreview();
    } catch {
      toast("Error al aplicar transformación", "error");
    } finally {
      setApplying(false);
    }
  }

  async function fetchHistory() {
    try {
      const res = await apiFetch("/transformations/history?limit=10");
      if (res.ok) setHistory(await res.json());
    } catch { /* non-critical */ }
  }

  useEffect(() => { fetchHistory(); }, []);

  const changedCount = preview.filter((r) => r.original !== r.transformed && !r.error).length;

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      <PageHeader
        title="Transformations"
        description="Aplica expresiones en bulk sobre cualquier campo sin escribir código."
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* ── Config panel ── */}
        <div className="lg:col-span-1 flex flex-col gap-4">

          {/* Field selector */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 flex flex-col gap-3">
            <label className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Campo</label>
            <select
              value={field}
              onChange={(e) => setField(e.target.value)}
              className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              {FIELDS.map((f) => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>

          {/* Expression editor */}
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4 flex flex-col gap-3">
            <label className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Expresión</label>
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                value={expression}
                onChange={(e) => { setExpression(e.target.value); setShowAutocomplete(true); }}
                onFocus={() => setShowAutocomplete(true)}
                onBlur={() => setTimeout(() => setShowAutocomplete(false), 200)}
                placeholder="value.trim()"
                className="w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 px-3 py-2 font-mono text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              {showAutocomplete && filteredFns.length > 0 && (
                <ul className="absolute z-20 mt-1 w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg max-h-52 overflow-y-auto">
                  {filteredFns.map((fn) => (
                    <li key={fn.expr}>
                      <button
                        type="button"
                        onMouseDown={() => { setExpression(fn.expr); setShowAutocomplete(false); }}
                        className="w-full text-left px-3 py-2 hover:bg-indigo-50 dark:hover:bg-indigo-900/30"
                      >
                        <span className="font-mono text-xs text-indigo-700 dark:text-indigo-300">{fn.label}</span>
                        <span className="ml-2 text-xs text-gray-400">{fn.desc}</span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <button
              onClick={runPreview}
              disabled={previewLoading}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
            >
              {previewLoading ? "Calculando…" : "Vista previa"}
            </button>
          </div>

          {/* Apply */}
          {preview.length > 0 && (
            <div className="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 p-4 flex flex-col gap-3">
              <p className="text-sm text-amber-800 dark:text-amber-300">
                <strong>{changedCount}</strong> de {preview.length} filas (muestra) cambiarán.
              </p>
              <button
                onClick={() => setConfirmOpen(true)}
                disabled={applying || changedCount === 0}
                className="rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white hover:bg-amber-700 disabled:opacity-50 transition-colors"
              >
                {applying ? "Aplicando…" : "Aplicar a todo el dominio"}
              </button>
              {lastResult && (
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Última aplicación: <strong>{lastResult.affected}</strong> / {lastResult.total} filas modificadas.
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Preview table ── */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-700">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">Vista previa (muestra 20)</span>
              {preview.length > 0 && (
                <span className="text-xs text-gray-400">{changedCount} cambios detectados</span>
              )}
            </div>

            {preview.length === 0 ? (
              <div className="flex items-center justify-center h-40 text-sm text-gray-400">
                Selecciona un campo y expresión, luego haz clic en &quot;Vista previa&quot;.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead className="bg-gray-50 dark:bg-gray-900/50">
                    <tr>
                      <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-400 w-1/2">Antes</th>
                      <th className="px-4 py-2 text-left font-medium text-gray-500 dark:text-gray-400 w-1/2">Después</th>
                    </tr>
                  </thead>
                  <tbody>
                    {preview.map((row, i) => (
                      <tr key={i} className={`border-t border-gray-100 dark:border-gray-700 ${row.error ? "bg-red-50 dark:bg-red-900/10" : row.original !== row.transformed ? "bg-emerald-50/40 dark:bg-emerald-900/10" : ""}`}>
                        <td className="px-4 py-2 font-mono text-gray-600 dark:text-gray-400 truncate max-w-xs">
                          {row.original ?? <span className="italic text-gray-300">null</span>}
                        </td>
                        <td className="px-4 py-2 font-mono truncate max-w-xs">
                          {row.error
                            ? <span className="text-red-600 dark:text-red-400 text-[10px]">&#9888; {row.error}</span>
                            : <DiffCell original={row.original} transformed={row.transformed} />
                          }
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* History */}
          {history.length > 0 && (
            <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-100 dark:border-gray-700">
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-200">Historial reciente</span>
              </div>
              <ul className="divide-y divide-gray-100 dark:divide-gray-700">
                {history.map((h) => (
                  <li key={h.id} className="px-4 py-2.5 flex items-center justify-between gap-3">
                    <div className="flex flex-col gap-0.5 min-w-0">
                      <span className="font-mono text-xs text-indigo-700 dark:text-indigo-300 truncate">{h.params.expression}</span>
                      <span className="text-[10px] text-gray-400">
                        campo: <strong>{h.params.field}</strong>{h.params.domain_id ? ` · dominio: ${h.params.domain_id}` : ""}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      <span className="text-xs text-gray-500">{h.affected_count} filas</span>
                      {h.reverted && <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-500">revertido</span>}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Confirm modal */}
      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 p-6 w-full max-w-sm shadow-xl">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">Confirmar transformación</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
              Campo: <strong className="text-gray-800 dark:text-gray-200">{field}</strong>
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Expresión: <code className="text-xs bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded font-mono">{expression}</code>
            </p>
            <p className="text-sm text-amber-700 dark:text-amber-400 mb-4">
              Esta acción modificará <strong>todas</strong> las entidades del dominio activo que tengan valor en este campo.
            </p>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setConfirmOpen(false)} className="px-4 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
                Cancelar
              </button>
              <button onClick={runApply} className="px-4 py-2 rounded-lg text-sm font-medium bg-amber-600 text-white hover:bg-amber-700">
                Aplicar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
