"use client";

import { useEffect, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import type { ToastVariant } from "../components/ui";
import { apiFetch } from "@/lib/api";

type NotificationForm = {
    smtp_host: string;
    smtp_port: number;
    smtp_user: string;
    smtp_password: string;
    from_email: string;
    recipient_email: string;
    enabled: boolean;
    notify_on_enrichment_batch: boolean;
    notify_on_authority_confirm: boolean;
};

type NotificationFieldConfig = {
    label: string;
    key: keyof NotificationForm;
    type: "text" | "number" | "email" | "password";
    placeholder: string;
};

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function NotificationsTab({
    toast,
}: {
    toast: (msg: string, v?: ToastVariant) => void;
}) {
    const { t } = useLanguage();
    const tr = (key: string, fallback: string) => {
        const value = t(key);
        return value === key ? fallback : value;
    };
    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";
    const fieldConfigs: NotificationFieldConfig[] = [
        { label: t("settings.notifications.smtp_host"), key: "smtp_host", type: "text", placeholder: "smtp.gmail.com" },
        { label: t("settings.notifications.smtp_port"), key: "smtp_port", type: "number", placeholder: "587" },
        { label: t("settings.notifications.smtp_user"), key: "smtp_user", type: "text", placeholder: "user@example.com" },
        { label: t("settings.notifications.smtp_password"), key: "smtp_password", type: "password", placeholder: t("settings.notifications.smtp_password_placeholder") },
        { label: t("settings.notifications.from_email"), key: "from_email", type: "email", placeholder: "noreply@example.com" },
        { label: t("settings.notifications.recipient_email"), key: "recipient_email", type: "email", placeholder: "admin@example.com" },
    ];
    const toggleConfigs: Array<{ label: string; key: keyof Pick<NotificationForm, "enabled" | "notify_on_enrichment_batch" | "notify_on_authority_confirm"> }> = [
        { label: t("settings.notifications.toggle_enabled"), key: "enabled" },
        { label: t("settings.notifications.toggle_enrichment"), key: "notify_on_enrichment_batch" },
        { label: t("settings.notifications.toggle_authority"), key: "notify_on_authority_confirm" },
    ];

    const [form, setForm] = useState<NotificationForm>({
        smtp_host: "",
        smtp_port: 587,
        smtp_user: "",
        smtp_password: "",
        from_email: "",
        recipient_email: "",
        enabled: false,
        notify_on_enrichment_batch: true,
        notify_on_authority_confirm: true,
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const missingRequiredFields = !form.smtp_host || !form.from_email || !form.recipient_email;

    useEffect(() => {
        let mounted = true;

        void (async () => {
            try {
                const response = await apiFetch("/notifications/settings");
                if (!response.ok) {
                    throw new Error(t("settings.notifications.toast.load_failed"));
                }
                const data = await response.json() as Partial<NotificationForm>;
                if (!mounted) return;
                setForm(prev => ({ ...prev, ...data, smtp_password: "" }));
            } catch (error: unknown) {
                toast(getErrorMessage(error, t("settings.notifications.toast.load_failed")), "error");
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        })();

        return () => {
            mounted = false;
        };
    }, [t, toast]);

    const setField = <K extends keyof NotificationForm>(key: K, value: NotificationForm[K]) => {
        setForm(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const payload: Partial<NotificationForm> = { ...form };
            if (!payload.smtp_password) {
                delete payload.smtp_password;
            }
            const response = await apiFetch("/notifications/settings", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const errorBody = await response.json().catch(() => ({ detail: t("settings.notifications.toast.save_failed") })) as { detail?: string };
                throw new Error(errorBody.detail || t("settings.notifications.toast.save_failed"));
            }
            toast(t("settings.notifications.toast.saved"), "success");
        } catch (error: unknown) {
            toast(getErrorMessage(error, t("settings.notifications.toast.save_failed")), "error");
        } finally {
            setSaving(false);
        }
    };

    const handleTest = async () => {
        if (missingRequiredFields) {
            toast(tr("settings.notifications.toast.test_requires_fields", "Add SMTP host, sender, and recipient before sending a test."), "warning");
            return;
        }
        setTesting(true);
        try {
            const response = await apiFetch("/notifications/test", { method: "POST" });
            const data = await response.json().catch(() => ({ sent: false })) as { sent?: boolean };
            if (data.sent) {
                toast(t("settings.notifications.toast.test_sent"), "success");
            } else {
                toast(t("settings.notifications.toast.test_not_sent"), "warning");
            }
        } catch {
            toast(t("settings.notifications.toast.test_failed"), "error");
        } finally {
            setTesting(false);
        }
    };

    if (loading) {
        return <div className="py-10 text-center text-sm text-gray-400">{t("common.loading")}</div>;
    }

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-blue-100 bg-blue-50/70 p-4 shadow-sm dark:border-blue-900/30 dark:bg-blue-900/10">
                <p className="text-sm font-semibold text-blue-950 dark:text-blue-100">
                    {tr("settings.notifications.guidance_title", "Set up email delivery before relying on alerts")}
                </p>
                <p className="mt-1 text-xs text-blue-900/80 dark:text-blue-200/80">
                    {tr("settings.notifications.guidance_body", "Use SMTP settings that can send from this workspace. A test message helps confirm delivery before enabling operational alerts.")}
                </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-gray-500 dark:text-gray-400">
                        {tr("settings.notifications.summary.enabled", "Alerts")}
                    </p>
                    <p className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
                        {form.enabled ? tr("settings.notifications.summary.enabled_on", "Enabled") : tr("settings.notifications.summary.enabled_off", "Disabled")}
                    </p>
                </div>
                <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-gray-500 dark:text-gray-400">
                        {tr("settings.notifications.summary.sender", "Sender")}
                    </p>
                    <p className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
                        {form.from_email || tr("common.none", "None")}
                    </p>
                </div>
                <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-gray-500 dark:text-gray-400">
                        {tr("settings.notifications.summary.recipient", "Recipient")}
                    </p>
                    <p className="mt-2 text-sm font-semibold text-gray-900 dark:text-white">
                        {form.recipient_email || tr("common.none", "None")}
                    </p>
                </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">{t("settings.notifications.smtp_config")}</h3>
                <p className="mb-4 text-xs text-gray-500 dark:text-gray-400">
                    {tr("settings.notifications.smtp_help", "These values are used for test messages and notification delivery from this workspace. Leave the password blank to keep the stored secret.")}
                </p>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {fieldConfigs.map(({ label, key, type, placeholder }) => (
                        <div key={key}>
                            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">{label}</label>
                            <input
                                type={type}
                                className={inputClass}
                                value={String(form[key])}
                                onChange={event => {
                                    const nextValue = type === "number" ? Number(event.target.value) : event.target.value;
                                    setField(key, nextValue as NotificationForm[typeof key]);
                                }}
                                placeholder={placeholder}
                            />
                        </div>
                    ))}
                </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">{t("settings.notifications.alert_preferences")}</h3>
                <p className="mb-4 text-xs text-gray-500 dark:text-gray-400">
                    {tr("settings.notifications.preferences_help", "Turn on only the alerts that should surface outside the app. These settings affect future events after you save them.")}
                </p>
                <div className="space-y-3">
                    {toggleConfigs.map(({ label, key }) => (
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
                    {saving ? t("settings.notifications.saving") : t("settings.notifications.save")}
                </button>
                <button
                    onClick={handleTest}
                    disabled={testing || missingRequiredFields}
                    className="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                    {testing ? t("settings.notifications.sending") : t("settings.notifications.send_test")}
                </button>
            </div>
            {missingRequiredFields && (
                <p className="text-xs text-amber-600 dark:text-amber-400">
                    {tr("settings.notifications.test_hint", "Add SMTP host, sender, and recipient to enable the test email action.")}
                </p>
            )}
        </div>
    );
}
