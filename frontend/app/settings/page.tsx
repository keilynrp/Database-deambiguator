"use client";

import { useState, useEffect } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { useTheme } from "../contexts/ThemeContext";
import type { Language } from "../i18n/translations";
type Theme = "light" | "dark";
import { useAuth } from "../contexts/AuthContext";
import { PageHeader, TabNav, Badge, useToast } from "../components/ui";
import { apiFetch } from "@/lib/api";
import AvatarUpload from "../components/AvatarUpload";
import PasswordStrength from "../components/PasswordStrength";
import BrandingTab from "./BrandingTab";
import UsersTab from "./UsersTab";
import { ROLE_LABELS, ROLE_VARIANTS, type UserRole } from "./userManagementTypes";

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

// ── Tab: Account ─────────────────────────────────────────────────────────────

function AccountTab({ user, updateAvatarUrl, toast }: { user: any; updateAvatarUrl: (url: string | null) => void; toast: (msg: string, v?: any) => void }) {
    // ── Profile edit state ────────────────────────────────────────────────────
    const { refreshUser } = useAuth();
    const [displayName, setDisplayName] = useState(user?.display_name ?? "");
    const [email, setEmail]             = useState(user?.email ?? "");
    const [bio, setBio]                 = useState(user?.bio ?? "");
    const [profileSaving, setProfileSaving] = useState(false);

    // Keep form in sync if user object updates (e.g. after avatar upload refreshes user)
    useEffect(() => {
        setDisplayName(user?.display_name ?? "");
        setEmail(user?.email ?? "");
        setBio(user?.bio ?? "");
    }, [user?.display_name, user?.email, user?.bio]);

    async function handleSaveProfile(e: React.FormEvent) {
        e.preventDefault();
        setProfileSaving(true);
        try {
            const body: Record<string, string> = {};
            if (displayName !== (user?.display_name ?? "")) body.display_name = displayName;
            if (email !== (user?.email ?? ""))               body.email        = email;
            if (bio !== (user?.bio ?? ""))                   body.bio          = bio;
            if (Object.keys(body).length === 0) {
                toast("No changes to save", "info");
                return;
            }
            const res = await apiFetch("/users/me/profile", {
                method: "PATCH",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body),
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to save profile");
            }
            await refreshUser();
            toast("Profile updated successfully", "success");
        } catch (err: any) {
            toast(err.message || "Error saving profile", "error");
        } finally {
            setProfileSaving(false);
        }
    }

    // ── Password change state ─────────────────────────────────────────────────
    const [currentPw, setCurrentPw] = useState("");
    const [newPw, setNewPw] = useState("");
    const [confirmPw, setConfirmPw] = useState("");
    const [pwSaving, setPwSaving] = useState(false);

    async function handleChangePassword(e: React.FormEvent) {
        e.preventDefault();
        if (newPw.length < 8) {
            toast("New password must be at least 8 characters", "error");
            return;
        }
        if (newPw !== confirmPw) {
            toast("Passwords do not match", "error");
            return;
        }
        setPwSaving(true);
        try {
            const res = await apiFetch("/users/me/password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ current_password: currentPw, new_password: newPw }),
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to change password");
            }
            toast("Password updated successfully", "success");
            setCurrentPw("");
            setNewPw("");
            setConfirmPw("");
        } catch (err: any) {
            toast(err.message || "Error changing password", "error");
        } finally {
            setPwSaving(false);
        }
    }

    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    return (
        <div className="space-y-4">
            {/* Avatar */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Profile Picture</h3>
                <AvatarUpload
                    username={user?.username ?? ""}
                    role={user?.role ?? "viewer"}
                    currentAvatarUrl={user?.avatar_url}
                    onUpdated={updateAvatarUrl}
                    toast={toast}
                />
            </div>

            {/* Profile info — editable */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-1 text-base font-semibold text-gray-900 dark:text-white">Profile</h3>
                <p className="mb-5 text-sm text-gray-500 dark:text-gray-400">Update your display name, email address, and bio.</p>

                {/* Read-only fields */}
                <div className="mb-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <div className="flex flex-col gap-1 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/50">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Username</span>
                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200">{user?.username}</span>
                    </div>
                    <div className="flex flex-col gap-1 rounded-xl border border-gray-100 bg-gray-50 p-4 dark:border-gray-800 dark:bg-gray-800/50">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-400">Role</span>
                        <Badge variant={ROLE_VARIANTS[user?.role as UserRole] ?? "default"}>
                            {ROLE_LABELS[user?.role as UserRole] ?? user?.role}
                        </Badge>
                    </div>
                </div>

                {/* Editable fields */}
                <form onSubmit={handleSaveProfile} className="space-y-4 max-w-lg">
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Display name <span className="text-gray-400 font-normal">(optional)</span>
                        </label>
                        <input
                            type="text"
                            className={inputClass}
                            value={displayName}
                            onChange={e => setDisplayName(e.target.value)}
                            maxLength={100}
                            placeholder="Your full name or nickname"
                            autoComplete="name"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Email address
                        </label>
                        <input
                            type="email"
                            className={inputClass}
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            maxLength={255}
                            placeholder="you@example.com"
                            autoComplete="email"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Bio <span className="text-gray-400 font-normal">(max 500 chars)</span>
                        </label>
                        <textarea
                            className="w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-900 outline-none transition-colors focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white resize-none"
                            rows={3}
                            value={bio}
                            onChange={e => setBio(e.target.value)}
                            maxLength={500}
                            placeholder="A short description about yourself…"
                        />
                        <p className="mt-1 text-right text-xs text-gray-400">{bio.length}/500</p>
                    </div>
                    <button
                        type="submit"
                        disabled={profileSaving}
                        className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                        {profileSaving && (
                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        )}
                        {profileSaving ? "Saving…" : "Save Profile"}
                    </button>
                </form>
            </div>

            {/* Change password */}
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Change Password</h3>
                <form onSubmit={handleChangePassword} className="space-y-4 max-w-sm">
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Current password
                        </label>
                        <input
                            type="password"
                            className={inputClass}
                            value={currentPw}
                            onChange={e => setCurrentPw(e.target.value)}
                            required
                            autoComplete="current-password"
                        />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            New password
                        </label>
                        <input
                            type="password"
                            className={inputClass}
                            value={newPw}
                            onChange={e => setNewPw(e.target.value)}
                            required
                            minLength={8}
                            autoComplete="new-password"
                        />
                        <PasswordStrength password={newPw} />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-sm font-medium text-gray-700 dark:text-gray-300">
                            Confirm new password
                        </label>
                        <input
                            type="password"
                            className={`${inputClass} ${confirmPw && confirmPw !== newPw ? "border-red-400 focus:border-red-500 focus:ring-red-400" : ""}`}
                            value={confirmPw}
                            onChange={e => setConfirmPw(e.target.value)}
                            required
                            autoComplete="new-password"
                        />
                        {confirmPw && confirmPw !== newPw && (
                            <p className="mt-1 text-xs text-red-500">Passwords do not match</p>
                        )}
                    </div>
                    <button
                        type="submit"
                        disabled={pwSaving || !currentPw || !newPw || newPw !== confirmPw}
                        className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
                    >
                        {pwSaving && (
                            <svg className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                        )}
                        {pwSaving ? "Saving…" : "Update Password"}
                    </button>
                </form>
            </div>
        </div>
    );
}

// ── Tab: User Management ──────────────────────────────────────────────────────

function WebhooksTab({ toast }: { toast: (msg: string, v?: "success" | "error" | "warning" | "info") => void }) {
    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-indigo-200 bg-gradient-to-br from-indigo-50/80 to-white p-8 shadow-sm dark:border-indigo-500/20 dark:from-indigo-500/5 dark:to-gray-900">
                <div className="flex items-center gap-4">
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-100 dark:bg-indigo-500/15">
                        <svg className="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Webhooks Management</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            Configure outbound HTTP callbacks, view delivery history, and send test pings.
                        </p>
                    </div>
                </div>
                <a
                    href="/settings/webhooks"
                    className="mt-6 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-all hover:bg-indigo-700 hover:shadow-md"
                >
                    Open Webhooks Panel
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                </a>
            </div>
        </div>
    );
}

// ── Tab: Notifications ────────────────────────────────────────────────────────

function NotificationsTab({ toast }: { toast: (msg: string, v?: any) => void }) {
    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    const [form, setForm] = useState({
        smtp_host: "", smtp_port: 587, smtp_user: "", smtp_password: "",
        from_email: "", recipient_email: "", enabled: false,
        notify_on_enrichment_batch: true, notify_on_authority_confirm: true,
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);

    useEffect(() => {
        apiFetch("/notifications/settings").then(async r => {
            if (r.ok) {
                const d = await r.json();
                setForm(f => ({ ...f, ...d, smtp_password: "" }));
            }
        }).finally(() => setLoading(false));
    }, []);

    const handleSave = async () => {
        setSaving(true);
        try {
            const payload: Record<string, any> = { ...form };
            if (!payload.smtp_password) delete payload.smtp_password;
            const r = await apiFetch("/notifications/settings", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!r.ok) throw new Error((await r.json()).detail);
            toast("Notification settings saved", "success");
        } catch (e: any) {
            toast(e.message || "Save failed", "error");
        } finally { setSaving(false); }
    };

    const handleTest = async () => {
        setTesting(true);
        try {
            const r = await apiFetch("/notifications/test", { method: "POST" });
            const d = await r.json();
            if (d.sent) toast("Test email sent successfully", "success");
            else toast("Email not sent — check settings and ensure alerts are enabled", "warning");
        } catch { toast("Test failed", "error"); }
        finally { setTesting(false); }
    };

    const setField = (k: keyof typeof form, v: any) => setForm(prev => ({ ...prev, [k]: v }));

    if (loading) return <div className="py-10 text-center text-sm text-gray-400">Loading…</div>;

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">SMTP Configuration</h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {([
                        { label: "SMTP Host", key: "smtp_host", type: "text", placeholder: "smtp.gmail.com" },
                        { label: "SMTP Port", key: "smtp_port", type: "number", placeholder: "587" },
                        { label: "SMTP User", key: "smtp_user", type: "text", placeholder: "user@example.com" },
                        { label: "SMTP Password", key: "smtp_password", type: "password", placeholder: "Leave blank to keep existing" },
                        { label: "From Email", key: "from_email", type: "email", placeholder: "noreply@example.com" },
                        { label: "Recipient Email", key: "recipient_email", type: "email", placeholder: "admin@example.com" },
                    ] as const).map(({ label, key, type, placeholder }) => (
                        <div key={key}>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{label}</label>
                            <input
                                type={type}
                                className={inputClass}
                                value={String(form[key])}
                                onChange={e => setField(key, type === "number" ? Number(e.target.value) : e.target.value)}
                                placeholder={placeholder}
                            />
                        </div>
                    ))}
                </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Alert Preferences</h3>
                <div className="space-y-3">
                    {([
                        { label: "Enable email alerts", key: "enabled" },
                        { label: "Notify on enrichment batch complete", key: "notify_on_enrichment_batch" },
                        { label: "Notify on authority record confirmed", key: "notify_on_authority_confirm" },
                    ] as const).map(({ label, key }) => (
                        <label key={key} className="flex cursor-pointer items-center gap-3">
                            <div
                                onClick={() => setField(key, !form[key])}
                                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${form[key] ? "bg-indigo-600" : "bg-gray-300 dark:bg-gray-600"}`}
                            >
                                <span className={`inline-block h-3.5 w-3.5 rounded-full bg-white shadow transition-transform ${form[key] ? "translate-x-4" : "translate-x-1"}`} />
                            </div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
                        </label>
                    ))}
                </div>
            </div>

            <div className="flex items-center gap-3">
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                    {saving ? "Saving…" : "Save Settings"}
                </button>
                <button
                    onClick={handleTest}
                    disabled={testing}
                    className="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                    {testing ? "Sending…" : "Send Test Email"}
                </button>
            </div>
        </div>
    );
}

