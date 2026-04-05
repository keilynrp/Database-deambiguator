"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useTheme } from "../contexts/ThemeContext";
import type { Language } from "../i18n/translations";
type Theme = "light" | "dark";
import { useAuth } from "../contexts/AuthContext";
import { PageHeader, TabNav, useToast } from "../components/ui";
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

// ── Tab: Preferences ─────────────────────────────────────────────────────────

function PreferencesTab({
    language, setLanguage, theme, setTheme, t,
}: {
    language: Language;
    setLanguage: (l: Language) => void;
    theme: Theme;
    setTheme: (t: Theme) => void;
    t: (k: string) => string;
}) {
    return (
        <div className="space-y-4">
            {/* Language */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex items-start justify-between">
                    <div>
                        <h3 className="text-base font-medium text-gray-900 dark:text-white">{t("settings.language")}</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t("settings.language.desc")}</p>
                    </div>
                    <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
                        {(["en", "es"] as const).map((lang) => (
                            <button
                                key={lang}
                                onClick={() => setLanguage(lang)}
                                className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                                    language === lang
                                        ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
                                        : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                                }`}
                            >
                                <span className="text-lg">{lang === "en" ? "🇺🇸" : "🇪🇸"}</span>
                                {lang === "en" ? "English" : "Español"}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Theme */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex items-start justify-between">
                    <div>
                        <h3 className="text-base font-medium text-gray-900 dark:text-white">{t("settings.theme")}</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t("settings.theme.desc")}</p>
                    </div>
                    <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
                        <button
                            onClick={() => setTheme("light" as Theme)}
                            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                                theme === "light"
                                    ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
                                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                            }`}
                        >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                            </svg>
                            {t("settings.theme.light")}
                        </button>
                        <button
                            onClick={() => setTheme("dark" as Theme)}
                            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                                theme === "dark"
                                    ? "bg-white text-gray-900 shadow-sm dark:bg-gray-700 dark:text-white"
                                    : "text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                            }`}
                        >
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                            </svg>
                            {t("settings.theme.dark")}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// ── Tab: User Management ──────────────────────────────────────────────────────
