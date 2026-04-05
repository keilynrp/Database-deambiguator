"use client";

import { useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useTheme } from "../contexts/ThemeContext";
import { useAuth } from "../contexts/AuthContext";
import { PageHeader, TabNav, useToast } from "../components/ui";
import PreferencesTab from "./PreferencesTab";
import BrandingTab from "./BrandingTab";
import AccountTab from "./AccountTab";
import NotificationsTab from "./NotificationsTab";
import UsersTab from "./UsersTab";
import WebhooksTab from "./WebhooksTab";

// ── Types ───────────────────────────────────────────────────────────────────

type Tab = "preferences" | "account" | "users" | "webhooks" | "notifications" | "branding";


// ── Main Page ────────────────────────────────────────────────────────────────

export default function SettingsPage() {
    const { language, setLanguage, t } = useLanguage();
    const { theme, setTheme } = useTheme();
    const { user, updateAvatarUrl } = useAuth();
    const { toast } = useToast();

    const isSuperAdmin = user?.role === "super_admin";

    const isAdmin = user?.role === "super_admin" || user?.role === "admin";

    const tabs = [
        { id: "preferences", label: "Preferences" },
        { id: "account",     label: "Account" },
        ...(isSuperAdmin ? [{ id: "users", label: "User Management" }] : []),
        ...(isAdmin ? [{ id: "webhooks",      label: "Webhooks" }] : []),
        ...(isAdmin ? [{ id: "notifications", label: "Notifications" }] : []),
        ...(isAdmin ? [{ id: "branding",      label: "Branding" }] : []),
    ];

    const [tab, setTab] = useState<Tab>("preferences");

    return (
        <div className="space-y-6">
            <PageHeader
                breadcrumbs={[{ label: "Home", href: "/" }, { label: "Settings" }]}
                title={t("settings.title")}
                description={t("settings.subtitle")}
            />

            <TabNav
                tabs={tabs}
                activeTab={tab}
                onTabChange={(id) => setTab(id as Tab)}
            />

            {tab === "preferences" && (
                <PreferencesTab
                    language={language}
                    setLanguage={setLanguage}
                    theme={theme}
                    setTheme={setTheme}
                    t={t}
                />
            )}
            {tab === "account"        && <AccountTab user={user} updateAvatarUrl={updateAvatarUrl} toast={toast} />}
            {tab === "users"          && isSuperAdmin && <UsersTab currentUserId={user?.id ?? 0} toast={toast} />}
            {tab === "webhooks"       && isAdmin && <WebhooksTab toast={toast} />}
            {tab === "notifications"  && isAdmin && <NotificationsTab toast={toast} />}
            {tab === "branding"       && isAdmin && <BrandingTab toast={toast} />}
        </div>
    );
}
