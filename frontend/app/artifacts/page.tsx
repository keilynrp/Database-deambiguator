"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { useDomain } from "../contexts/DomainContext";
import { PageHeader } from "../components/ui";

// ── Types ──────────────────────────────────────────────────────────────────────

interface GapSummary {
  critical: number;
  warning: number;
  ok: number;
  total_entities: number;
}

interface Template {
  id: number;
  name: string;
}

// ── Feature card ───────────────────────────────────────────────────────────────

function FeatureCard({
  title,
  description,
  icon,
  href,
  children,
  accent,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  children?: React.ReactNode;
  accent: string;
}) {
  return (
    <div className="flex flex-col rounded-2xl border border-gray-200 bg-white shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <div className={`flex items-center gap-3 rounded-t-2xl px-6 py-4 ${accent}`}>
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{title}</h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">{description}</p>
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-4 px-6 py-5">
        {children}
        <div className="mt-auto">
          <Link
            href={href}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors"
          >
            Open
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function ArtifactStudioPage() {
  const { activeDomainId } = useDomain();
  const [gapSummary, setGapSummary] = useState<GapSummary | null>(null);
  const [templateCount, setTemplateCount] = useState<number | null>(null);
  const [loadingGaps, setLoadingGaps] = useState(true);
  const [loadingTemplates, setLoadingTemplates] = useState(true);

  useEffect(() => {
    if (!activeDomainId) return;
    apiFetch(`/artifacts/gaps/${activeDomainId}`)
      .then((r) => r.ok ? r.json() : null)
      .then((d) => d ? setGapSummary(d.summary) : null)
      .finally(() => setLoadingGaps(false));
  }, [activeDomainId]);

  useEffect(() => {
    apiFetch("/artifacts/templates")
      .then((r) => r.ok ? r.json() : [])
      .then((d: Template[]) => setTemplateCount(d.length))
      .finally(() => setLoadingTemplates(false));
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        breadcrumbs={[
          { label: "Home", href: "/" },
          { label: "Artifact Studio" },
        ]}
        title="Artifact Studio"
        description="Build and export strategic intelligence artifacts powered by your data"
      />

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">

        {/* Gap Detector */}
        <FeatureCard
          title="Knowledge Gap Detector"
          description="Identify and prioritize data quality issues"
          icon="🔍"
          href="/artifacts/gaps"
          accent="bg-red-50 dark:bg-red-900/10"
        >
          {loadingGaps ? (
            <div className="flex gap-3">
              {[1, 2].map((i) => (
                <div key={i} className="h-14 flex-1 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />
              ))}
            </div>
          ) : gapSummary ? (
            <div className="flex gap-3">
              <div className="flex flex-1 flex-col items-center rounded-xl border border-red-200 bg-red-50 py-3 dark:border-red-800 dark:bg-red-900/10">
                <span className="text-xl font-bold text-red-600 dark:text-red-400">{gapSummary.critical}</span>
                <span className="text-xs text-red-700 dark:text-red-400">Critical</span>
              </div>
              <div className="flex flex-1 flex-col items-center rounded-xl border border-amber-200 bg-amber-50 py-3 dark:border-amber-800 dark:bg-amber-900/10">
                <span className="text-xl font-bold text-amber-600 dark:text-amber-400">{gapSummary.warning}</span>
                <span className="text-xs text-amber-700 dark:text-amber-400">Warnings</span>
              </div>
              <div className="flex flex-1 flex-col items-center rounded-xl border border-green-200 bg-green-50 py-3 dark:border-green-800 dark:bg-green-900/10">
                <span className="text-xl font-bold text-green-600 dark:text-green-400">{gapSummary.ok}</span>
                <span className="text-xs text-green-700 dark:text-green-400">OK</span>
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-400 dark:text-gray-500">No data loaded</p>
          )}
          {gapSummary && (
            <p className="text-xs text-gray-400 dark:text-gray-500">
              {gapSummary.total_entities.toLocaleString()} total entities in domain
            </p>
          )}
        </FeatureCard>

        {/* Report Builder */}
        <FeatureCard
          title="Report Builder"
          description="PDF · Excel · PowerPoint with built-in templates"
          icon="📋"
          href="/reports"
          accent="bg-blue-50 dark:bg-blue-900/10"
        >
          {loadingTemplates ? (
            <div className="h-12 animate-pulse rounded-xl bg-gray-100 dark:bg-gray-800" />
          ) : (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 dark:border-blue-800 dark:bg-blue-900/10">
                <span className="text-xl font-bold text-blue-600 dark:text-blue-400">{templateCount ?? 0}</span>
                <span className="text-sm text-blue-700 dark:text-blue-300">Templates available</span>
              </div>
              <div className="flex gap-2">
                {["HTML", "PDF", "Excel", "PPT"].map((fmt) => (
                  <span
                    key={fmt}
                    className="rounded-lg border border-gray-200 bg-white px-2 py-1 text-xs font-medium text-gray-600 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400"
                  >
                    {fmt}
                  </span>
                ))}
              </div>
            </div>
          )}
        </FeatureCard>

        {/* ROI Projector */}
        <FeatureCard
          title="ROI Projector"
          description="Monte Carlo simulation · P10/P50/P90 · CSV export"
          icon="📈"
          href="/analytics/roi"
          accent="bg-violet-50 dark:bg-violet-900/10"
        >
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-3 rounded-xl border border-violet-200 bg-violet-50 px-4 py-3 dark:border-violet-800 dark:bg-violet-900/10">
              <span className="text-lg">🎲</span>
              <div>
                <p className="text-sm font-medium text-violet-700 dark:text-violet-300">Monte Carlo Engine</p>
                <p className="text-xs text-violet-600 dark:text-violet-400">10,000-run probability simulation</p>
              </div>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Project ROI scenarios across enrichment and harmonization investments
            </p>
          </div>
        </FeatureCard>

      </div>
    </div>
  );
}
