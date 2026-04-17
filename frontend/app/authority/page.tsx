"use client";

import { useState } from "react";
import Link from "next/link";
import { PageHeader, TabNav } from "../components/ui";
import { useDomain } from "../contexts/DomainContext";
import { useLanguage } from "../contexts/LanguageContext";
import DisambiguationTab from "./DisambiguationTab";
import ReviewQueueTab from "./ReviewQueueTab";

export default function AuthorityPage() {
    const { activeDomain } = useDomain();
    const { t } = useLanguage();
    const [tab, setTab] = useState<"disambiguation" | "review">("disambiguation");

    const tabs = [
        { id: "disambiguation" as const, label: t("page.authority.tab_groups") },
        { id: "review" as const, label: t("page.authority.tab_review_queue") },
    ];

    return (
        <div className="space-y-6">
            <PageHeader
                breadcrumbs={[{ label: "Home", href: "/" }, { label: t("page.authority.breadcrumb") }]}
                title={t("page.authority.title")}
                description={t("page.authority.description")}
            />

            <div className="rounded-2xl border border-amber-200 bg-amber-50 p-5 shadow-sm dark:border-amber-900/40 dark:bg-amber-950/20">
                <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <div className="max-w-2xl">
                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700 dark:text-amber-300">
                            {t("page.authority.guided.eyebrow")}
                        </p>
                        <h2 className="mt-2 text-lg font-semibold text-amber-950 dark:text-amber-100">
                            {t("page.authority.guided.title")}
                        </h2>
                        <p className="mt-1 text-sm text-amber-800 dark:text-amber-200">
                            {tab === "disambiguation"
                                ? t("page.authority.guided.disambiguation")
                                : t("page.authority.guided.review")}
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <Link
                            href="/reports?preset=pilot-brief"
                            className="inline-flex items-center gap-2 rounded-lg bg-amber-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-amber-700"
                        >
                            {t("page.authority.guided.cta_reports")}
                        </Link>
                        <Link
                            href="/analytics/dashboard"
                            className="inline-flex items-center gap-2 rounded-lg border border-amber-300 bg-white px-4 py-2 text-sm font-medium text-amber-700 transition-colors hover:bg-amber-100 dark:border-amber-700 dark:bg-gray-900 dark:text-amber-300 dark:hover:bg-amber-950/30"
                        >
                            {t("page.authority.guided.cta_dashboard")}
                        </Link>
                    </div>
                </div>
            </div>

            <TabNav
                tabs={tabs}
                activeTab={tab}
                onTabChange={(id) => setTab(id as "disambiguation" | "review")}
            />

            {tab === "disambiguation" && <DisambiguationTab activeDomain={activeDomain} />}
            {tab === "review" && <ReviewQueueTab activeDomain={activeDomain} />}
        </div>
    );
}
