/* eslint-disable @next/next/no-img-element */
"use client";

import { useCallback, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";

const FAVICON_MAX_KB = 128;
const FAVICON_ACCEPT = "image/x-icon,image/vnd.microsoft.icon,image/png,image/svg+xml";

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

export default function FaviconDropZone({
    currentUrl,
    onUploaded,
    onRemove,
}: {
    currentUrl?: string | null;
    onUploaded: (url: string) => void | Promise<void>;
    onRemove: () => void | Promise<void>;
}) {
    const [dragging, setDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const upload = useCallback(async (file: File) => {
        setError(null);
        if (file.size > FAVICON_MAX_KB * 1024) {
            setError(`Favicon exceeds ${FAVICON_MAX_KB} KB.`);
            return;
        }
        setUploading(true);
        try {
            const fd = new FormData();
            fd.append("file", file);
            const res = await apiFetch("/branding/favicon", {
                method: "POST",
                body: fd,
            });
            if (!res.ok) {
                const err = await res.json().catch(() => ({ detail: "Upload failed" }));
                throw new Error(err.detail ?? "Upload failed");
            }
            const data = await res.json();
            await onUploaded(data.favicon_url);
        } catch (error: unknown) {
            setError(getErrorMessage(error, "Upload failed"));
        } finally {
            setUploading(false);
        }
    }, [onUploaded]);

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
            await apiFetch("/branding/favicon", { method: "DELETE" });
            await onRemove();
        } catch {
            setError("Failed to remove favicon.");
        }
    }

    const apiBase = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");
    const previewUrl = currentUrl?.startsWith("/static/")
        ? `${apiBase}${currentUrl}`
        : currentUrl;

    return (
        <div>
            <label className="mb-1.5 block text-xs font-medium text-gray-600 dark:text-gray-400">
                Favicon
                <span className="ml-1 font-normal text-gray-400">(ICO, PNG, SVG · max {FAVICON_MAX_KB} KB)</span>
            </label>
            <div
                onDragOver={e => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
                onDrop={handleDrop}
                onClick={() => !uploading && inputRef.current?.click()}
                className={`relative flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-5 transition-colors
                    ${dragging ? "border-indigo-400 bg-indigo-50 dark:bg-indigo-900/20" : "border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/40 dark:border-gray-700 dark:bg-gray-800/40 dark:hover:border-indigo-700"}`}
            >
                <input
                    ref={inputRef}
                    type="file"
                    accept={FAVICON_ACCEPT}
                    className="hidden"
                    onChange={handleChange}
                />
                {previewUrl ? (
                    <div className="mb-3 flex items-center gap-3">
                        <img
                            src={previewUrl}
                            alt="Current favicon"
                            className="h-8 w-8 object-contain"
                            onError={e => (e.currentTarget.hidden = true)}
                        />
                        <span className="text-xs text-gray-500 dark:text-gray-400">Current favicon</span>
                    </div>
                ) : null}
                {uploading ? (
                    <span className="text-sm text-indigo-600 dark:text-indigo-400">Uploading...</span>
                ) : (
                    <>
                        <p className="text-xs font-medium text-gray-700 dark:text-gray-300">Drop your favicon here</p>
                        <p className="mt-0.5 text-xs text-gray-400">or click to browse</p>
                    </>
                )}
            </div>
            {previewUrl && !uploading && (
                <button
                    type="button"
                    onClick={handleRemove}
                    className="mt-2 text-xs font-medium text-red-500 hover:text-red-700"
                >
                    Remove favicon
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
