/* eslint-disable @next/next/no-img-element */
"use client";

import { useCallback, useEffect, useState } from "react";
import { useBranding } from "../contexts/BrandingContext";
import { apiFetch } from "@/lib/api";
import FaviconDropZone from "./FaviconDropZone";
import LogoDropZone from "./LogoDropZone";

type ToastVariant = "success" | "error" | "warning" | "info" | "default";

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function BrandingTab({ toast }: { toast: (msg: string, v?: ToastVariant) => void }) {
    const { branding, refreshBranding } = useBranding();
    const inputClass = "h-10 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-900 outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-gray-700 dark:bg-gray-800 dark:text-white";

    const [form, setForm] = useState({
        platform_name: branding.platform_name,
        logo_url: branding.logo_url,
        favicon_url: branding.favicon_url,
        accent_color: branding.accent_color,
        footer_text: branding.footer_text,
    });
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        setForm({
            platform_name: branding.platform_name,
            logo_url: branding.logo_url,
            favicon_url: branding.favicon_url,
            accent_color: branding.accent_color,
            footer_text: branding.footer_text,
        });
    }, [branding]);

    const handleLogoUploaded = useCallback(async (url: string) => {
        setForm(prev => ({ ...prev, logo_url: url }));
        await refreshBranding();
        toast("Logo updated", "success");
    }, [refreshBranding, toast]);

    const handleLogoRemoved = useCallback(async () => {
        setForm(prev => ({ ...prev, logo_url: "" }));
        await refreshBranding();
        toast("Logo removed", "success");
    }, [refreshBranding, toast]);

    const handleFaviconUploaded = useCallback(async (url: string) => {
        setForm(prev => ({ ...prev, favicon_url: url }));
        await refreshBranding();
        toast("Favicon updated", "success");
    }, [refreshBranding, toast]);

    const handleFaviconRemoved = useCallback(async () => {
        setForm(prev => ({ ...prev, favicon_url: "" }));
        await refreshBranding();
        toast("Favicon removed", "success");
    }, [refreshBranding, toast]);

    const handleSave = async () => {
        setSaving(true);
        try {
            const r = await apiFetch("/branding/settings", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form),
            });
            if (!r.ok) {
                const err = await r.json();
                throw new Error(err.detail || "Save failed");
            }
            await refreshBranding();
            toast("Branding updated", "success");
        } catch (error: unknown) {
            toast(getErrorMessage(error, "Save failed"), "error");
        } finally {
            setSaving(false);
        }
    };

    const fld = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
        setForm(prev => ({ ...prev, [k]: e.target.value }));

    const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
    const previewLogoUrl = form.logo_url?.startsWith("/static/")
        ? `${apiBase}${form.logo_url}`
        : form.logo_url;

    return (
        <div className="space-y-4">
            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-base font-semibold text-gray-900 dark:text-white">Platform Identity</h3>
                <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                    <div>
                        <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">Platform Name</label>
                        <input className={inputClass} value={form.platform_name} onChange={fld("platform_name")} placeholder="UKIP" />
                    </div>
                    <div>
                        <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">Accent Color</label>
                        <div className="flex items-center gap-2">
                            <input
                                type="color"
                                value={form.accent_color}
                                onChange={fld("accent_color")}
                                className="h-10 w-12 cursor-pointer rounded-lg border border-gray-200 bg-white p-1 dark:border-gray-700 dark:bg-gray-800"
                            />
                            <input className={inputClass} value={form.accent_color} onChange={fld("accent_color")} placeholder="#6366f1" />
                        </div>
                    </div>

                    <div className="sm:col-span-2">
                        <LogoDropZone
                            currentUrl={form.logo_url}
                            accentColor={form.accent_color}
                            onUploaded={handleLogoUploaded}
                            onRemove={handleLogoRemoved}
                        />
                    </div>

                    <div className="sm:col-span-2">
                        <FaviconDropZone
                            currentUrl={form.favicon_url}
                            onUploaded={handleFaviconUploaded}
                            onRemove={handleFaviconRemoved}
                        />
                    </div>

                    <div className="sm:col-span-2">
                        <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">Footer Text</label>
                        <input className={inputClass} value={form.footer_text} onChange={fld("footer_text")} placeholder="Universal Knowledge Intelligence Platform" />
                    </div>
                </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h3 className="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Preview</h3>
                <div className="flex items-center gap-3 rounded-xl border border-gray-100 bg-gray-50 px-4 py-3 dark:border-gray-800 dark:bg-gray-800/50">
                    <div
                        className="flex h-8 w-8 items-center justify-center overflow-hidden rounded-lg"
                        style={{ backgroundColor: form.accent_color }}
                    >
                        {previewLogoUrl ? (
                            <img src={previewLogoUrl} alt="" className="h-full w-full object-contain p-0.5" onError={e => (e.currentTarget.hidden = true)} />
                        ) : (
                            <svg className="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                            </svg>
                        )}
                    </div>
                    <div>
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{form.platform_name || "UKIP"}</p>
                        <p className="text-xs text-gray-400">{form.footer_text}</p>
                    </div>
                </div>
            </div>

            <button
                onClick={handleSave}
                disabled={saving}
                className="rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            >
                {saving ? "Saving..." : "Save Branding"}
            </button>
        </div>
    );
}
