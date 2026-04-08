/* eslint-disable @next/next/no-img-element */
"use client";

import { useCallback, useRef, useState } from "react";
import { useLanguage } from "../contexts/LanguageContext";
import { apiFetch } from "@/lib/api";

const LOGO_MAX_KB = 512;
const LOGO_ACCEPT = "image/png,image/jpeg,image/svg+xml,image/webp";

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function LogoDropZone({
    currentUrl,
    accentColor,
    onUploaded,
    onRemove,
}: {
    currentUrl?: string | null;
    accentColor?: string;
    onUploaded: (url: string) => void | Promise<void>;
    onRemove: () => void | Promise<void>;
}) {
    const { t } = useLanguage();
    const [dragging, setDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

    const upload = useCallback(async (file: File) => {
        setError(null);
        if (file.size > LOGO_MAX_KB * 1024) {
            setError(t("settings.branding.logo_too_large", { size: LOGO_MAX_KB }));
            return;
        }
        setUploading(true);
        try {
            const fd = new FormData();
            fd.append("file", file);
            const res = await apiFetch("/branding/logo", {
                method: "POST",
                body: fd,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: t("settings.branding.upload_failed") }));
                throw new Error(err.detail ?? t("settings.branding.upload_failed"));
            }
            const data = await res.json();
            await onUploaded(data.logo_url);
        } catch (error: unknown) {
            setError(getErrorMessage(error, t("settings.branding.upload_failed")));
        } finally {
            setUploading(false);
        }
    }, [onUploaded, t]);

    function handleDrop(e: React.DragEvent) {
        e.preventDefault();
        setDragging(false);
        const file = e.dataTransfer.files[0];
        if (file) upload(file);
    }

    function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (file) upload(file);
        e.target.value = "";
    }

    async function handleRemove() {
        setError(null);
        try {
            await apiFetch("/branding/logo", { method: "DELETE" });
            await onRemove();
        } catch {
            setError(t("settings.branding.logo_remove_failed"));
        }
    }

    const previewUrl = currentUrl?.startsWith("/static/")
        ? `${apiBase}${currentUrl}`
        : currentUrl;

    return (
        <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">
                {t("settings.branding.logo")}
                <span className="ml-1 font-normal text-gray-400">({t("settings.branding.logo_help", { size: LOGO_MAX_KB })})</span>
            </label>
            <div
                onDragOver={e => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => !uploading && inputRef.current?.click()}
                className={`relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-6 transition-colors
                    ${dragging ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20" : "border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/40 dark:border-gray-700 dark:bg-gray-800/40 dark:hover:border-indigo-700"}`}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept={LOGO_ACCEPT}
                    className="hidden"
                    onChange={handleChange}
                />
                {previewUrl ? (
                    <div className="mb-3 flex items-center gap-3">
                        <div
                            className="flex h-10 w-10 items-center justify-center overflow-hidden rounded-lg"
                            style={{ backgroundColor: accentColor || "#6366f1" }}
                        >
                            <img
                                src={previewUrl}
                                alt={t("settings.branding.current_logo")}
                                className="h-full w-full object-contain p-1"
                                onError={e => (e.currentTarget.hidden = true)}
                            />
                        </div>
                        <span className="text-xs text-gray-500 dark:text-gray-400">{t("settings.branding.current_logo")}</span>
                    </div>
                ) : null}
                {uploading ? (
                    <span className="text-sm text-indigo-600 dark:text-indigo-400">{t("settings.branding.uploading")}</span>
                ) : (
                    <>
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">{t("settings.branding.logo_drop")}</p>
                        <p className="mt-0.5 text-xs text-gray-400">{t("settings.branding.or_click_browse")}</p>
                    </>
                )}
            </div>
            {previewUrl && !uploading && (
                <button
                    type="button"
                    onClick={handleRemove}
                    className="mt-2 text-xs font-medium text-red-500 hover:text-red-700"
                >
                    {t("settings.branding.remove_logo")}
                </button>
            )}
            {error && (
                <p className="mt-1.5 text-xs font-medium text-red-500">
                    {error}
                </p>
            )}
        </div>
    );
}
