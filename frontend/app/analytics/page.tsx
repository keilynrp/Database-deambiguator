"use client";

import { useCallback, useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

import { PageHeader } from "../components/ui";
import { useLanguage } from "../contexts/LanguageContext";
import { useDomain } from "../contexts/DomainContext";

import { AnalyticsEnrichmentSection } from "./AnalyticsEnrichmentSection";
import { AnalyticsOverviewSection } from "./AnalyticsOverviewSection";
import type { EnrichStats, Stats } from "./analyticsTypes";

export default function AnalyticsPage() {
  const { t } = useLanguage();
  const { activeDomainId } = useDomain();
  const [stats, setStats] = useState<Stats | null>(null);
  const [enrichStats, setEnrichStats] = useState<EnrichStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [enrichLoading, setEnrichLoading] = useState(true);
  const [bulkQueuing, setBulkQueuing] = useState(false);
  const [bulkResult, setBulkResult] = useState<{ queued_records: number } | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await apiFetch(`/olap/${activeDomainId}`);
      if (!response.ok) {
        throw new Error("Failed");
      }
      setStats(await response.json());
    } catch {
      // Keep current UX unchanged: silent fail with partial page rendering.
    } finally {
      setLoading(false);
    }
  }, [activeDomainId]);

  const fetchEnrichStats = useCallback(async () => {
    try {
      const response = await apiFetch("/enrich/stats");
      if (!response.ok) {
        throw new Error("Failed");
      }
      setEnrichStats(await response.json());
    } catch {
      // Keep current UX unchanged: silent fail with partial page rendering.
    } finally {
      setEnrichLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchStats();
    void fetchEnrichStats();
  }, [fetchStats, fetchEnrichStats]);

  const handleBulkEnrich = async () => {
    setBulkQueuing(true);
    setBulkResult(null);
    try {
      const response = await apiFetch("/enrich/bulk?limit=500", { method: "POST" });
      if (!response.ok) {
        throw new Error("Failed");
      }
      const data = await response.json();
      setBulkResult(data);
      setTimeout(() => {
        void fetchEnrichStats();
      }, 1500);
    } catch {
      // Keep current UX unchanged.
    } finally {
      setBulkQueuing(false);
    }
  };

  if (loading && enrichLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <svg className="h-8 w-8 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      </div>
    );
  }

  const totalCount = stats?.total_records ?? 0;

  return (
    <div className="space-y-8">
      <PageHeader
        breadcrumbs={[{ label: "Home", href: "/" }, { label: t("page.analytics.breadcrumb") }]}
        title={t("page.analytics.title")}
        description={t("page.analytics.description")}
      />

      <AnalyticsOverviewSection stats={stats} totalCount={totalCount} t={t} />
      <AnalyticsEnrichmentSection
        enrichStats={enrichStats}
        enrichLoading={enrichLoading}
        totalCount={totalCount}
        bulkQueuing={bulkQueuing}
        bulkResult={bulkResult}
        onBulkEnrich={handleBulkEnrich}
        t={t}
      />
    </div>
  );
}
