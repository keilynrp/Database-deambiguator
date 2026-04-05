"use client";

import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

type ToastVariant = "success" | "error" | "warning" | "info" | "default";

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

const FIELD_CONFIGS: NotificationFieldConfig[] = [
    { label: "SMTP Host", key: "smtp_host", type: "text", placeholder: "smtp.gmail.com" },
    { label: "SMTP Port", key: "smtp_port", type: "number", placeholder: "587" },
    { label: "SMTP User", key: "smtp_user", type: "text", placeholder: "user@example.com" },
    { label: "SMTP Password", key: "smtp_password", type: "password", placeholder: "Leave blank to keep existing" },
    { label: "From Email", key: "from_email", type: "email", placeholder: "noreply@example.com" },
    { label: "Recipient Email", key: "recipient_email", type: "email", placeholder: "admin@example.com" },
];

const TOGGLE_CONFIGS: Array<{ label: string; key: keyof Pick<NotificationForm, "enabled" | "notify_on_enrichment_batch" | "notify_on_authority_confirm"> }> = [
    { label: "Enable email alerts", key: "enabled" },
    { label: "Notify on enrichment batch complete", key: "notify_on_enrichment_batch" },
    { label: "Notify on authority record confirmed", key: "notify_on_authority_confirm" },
];

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function NotificationsTab({
    toast,
}: {
    toast: (msg: string, v?: ToastVariant) => void;
}) {
    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

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

    useEffect(() => {
        let mounted = true;

        void (async () => {
            try {
                const response = await apiFetch("/notifications/settings");
                if (!response.ok) {
                    throw new Error("Failed to load notification settings");
                }
                const data = await response.json() as Partial<NotificationForm>;
                if (!mounted) return;
                setForm(prev => ({ ...prev, ...data, smtp_password: "" }));
            } catch (error: unknown) {
                toast(getErrorMessage(error, "Failed to load notification settings"), "error");
            } finally {
                if (mounted) {
                    setLoading(false);
                }
            }
        })();

        return () => {
            mounted = false;
        };
    }, [toast]);

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
                const errorBody = await response.json().catch(() => ({ detail: "Save failed" })) as { detail?: string };
                throw new Error(errorBody.detail || "Save failed");
            }
            toast("Notification settings saved", "success");
        } catch (error: unknown) {
            toast(getErrorMessage(error, "Save failed"), "error");
        } finally {
            setSaving(false);
        }
    };

    const handleTest = async () => {
        setTesting(true);
        try {
            const response = await apiFetch("/notifications/test", { method: "POST" });
            const data = await response.json().catch(() => ({ sent: false })) as { sent?: boolean };
            if (data.sent) {
                toast("Test email sent successfully", "success");
            } else {
                toast("Email not sent — check settings and ensure alerts are enabled", "warning");
            }
        } catch {
            toast("Test failed", "error");
        } finally {
            setTesting(false);
        }
    };

    if (loading) {
        return <div className="py-10 text-center text-sm text-gray-400">Loading...</div>;
    }

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">SMTP Configuration</h3>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    {FIELD_CONFIGS.map(({ label, key, type, placeholder }) => (
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
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Alert Preferences</h3>
                <div className="space-y-3">
                    {TOGGLE_CONFIGS.map(({ label, key }) => (
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
                    {saving ? "Saving..." : "Save Settings"}
                </button>
                <button
                    onClick={handleTest}
                    disabled={testing}
                    className="rounded-xl border border-gray-200 px-5 py-2.5 text-sm font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-50 dark:border-gray-700 dark:text-gray-300 dark:hover:bg-gray-800"
                >
                    {testing ? "Sending..." : "Send Test Email"}
                </button>
            </div>
        </div>
    );
}
