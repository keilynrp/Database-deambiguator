"use client";

import { useState } from "react";
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
