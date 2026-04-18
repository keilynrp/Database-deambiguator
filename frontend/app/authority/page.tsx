"use client";

import { useState } from "react";
import { PageHeader, TabNav } from "../components/ui";
import PilotFlowCard from "../components/PilotFlowCard";
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

            <PilotFlowCard
                currentStep="review"
                tone="amber"
                title={t("page.authority.guided.title")}
                body={tab === "disambiguation"
                    ? t("page.authority.guided.disambiguation")
                    : t("page.authority.guided.review")}
                primaryCta={{
                    href: "/reports?preset=pilot-brief",
                    label: t("page.authority.guided.cta_reports"),
                }}
                secondaryCta={{
                    href: "/analytics/dashboard",
                    label: t("page.authority.guided.cta_dashboard"),
                }}
            />

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
