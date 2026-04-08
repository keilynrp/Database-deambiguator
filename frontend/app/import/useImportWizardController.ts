"use client";

import { useCallback, useState } from "react";
import { apiFetch } from "@/lib/api";
import type { ImportResult, PreviewData, WizardStep } from "./importWizardParts";

function getErrorMessage(error: unknown, fallback: string) {
    return error instanceof Error ? error.message : fallback;
}

async function parseErrorDetail(response: Response, fallback: string): Promise<string> {
    const contentType = response.headers.get("content-type") ?? "";
    if (contentType.includes("application/json")) {
        const errorBody = await response.json().catch(() => ({ detail: fallback })) as { detail?: unknown };
        return formatApiDetail(errorBody.detail, fallback);
    }

    const text = await response.text().catch(() => "");
    return text.trim() || fallback;
}

function formatApiDetail(detail: unknown, fallback: string): string {
    if (typeof detail === "string" && detail.trim()) {
        return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
        const first = detail[0];
        if (typeof first === "string") {
            return first;
        }
        if (first && typeof first === "object") {
            const msg = "msg" in first ? first.msg : null;
            const loc = "loc" in first && Array.isArray(first.loc) ? first.loc.join(" > ") : null;
            if (typeof msg === "string" && loc) {
                return `${loc}: ${msg}`;
            }
            if (typeof msg === "string") {
                return msg;
            }
        }
    }
    if (detail && typeof detail === "object") {
        if ("msg" in detail && typeof detail.msg === "string") {
            return detail.msg;
        }
        try {
            return JSON.stringify(detail);
        } catch {
            return fallback;
        }
    }
    return fallback;
}

export default function useImportWizardController() {
    const [step, setStep] = useState<WizardStep>(1);
    const [file, setFile] = useState<File | null>(null);
    const [previewing, setPreviewing] = useState(false);
    const [previewError, setPreviewError] = useState<string | null>(null);
    const [preview, setPreview] = useState<PreviewData | null>(null);
    const [mapping, setMapping] = useState<Record<string, string>>({});
    const [domain, setDomain] = useState("default");
    const [importing, setImporting] = useState(false);
    const [importResult, setImportResult] = useState<ImportResult | null>(null);
    const [importError, setImportError] = useState<string | null>(null);

    const handleFile = useCallback(async (nextFile: File) => {
        setFile(nextFile);
        setPreview(null);
        setPreviewError(null);
        setPreviewing(true);
        setStep(2);

        const form = new FormData();
        form.append("file", nextFile);

        try {
            const response = await apiFetch("/upload/preview", { method: "POST", body: form });
            if (!response.ok) {
                setPreviewError(await parseErrorDetail(response, "Preview failed"));
                return;
            }

            const data = await response.json() as PreviewData;
            setPreview(data);

            const initialMapping: Record<string, string> = {};
            for (const [column, model] of Object.entries(data.auto_mapping)) {
                initialMapping[column] = model ?? "";
            }
            setMapping(initialMapping);
        } catch (error: unknown) {
            setPreviewError(getErrorMessage(error, "Network error"));
        } finally {
            setPreviewing(false);
        }
    }, []);

    const handleImport = useCallback(async () => {
        if (!file) return;

        setImporting(true);
        setImportError(null);
        setStep(5);

        const form = new FormData();
        form.append("file", file);
        form.append("domain", domain);

        const cleanMapping: Record<string, string> = {};
        for (const [key, value] of Object.entries(mapping)) {
            if (value) cleanMapping[key] = value;
        }
        form.append("field_mapping", JSON.stringify(cleanMapping));

        try {
            const response = await apiFetch("/upload", { method: "POST", body: form });
            if (!response.ok) {
                setImportError(await parseErrorDetail(response, "Import failed"));
                return;
            }
            setImportResult(await response.json() as ImportResult);
        } catch (error: unknown) {
            setImportError(getErrorMessage(error, "Network error"));
        } finally {
            setImporting(false);
        }
    }, [domain, file, mapping]);

    const canNext: Record<WizardStep, boolean> = {
        1: Boolean(file),
        2: !previewing && !previewError && Boolean(preview),
        3: Boolean(domain),
        4: true,
        5: false,
    };

    const handleNext = useCallback(() => {
        if (step === 4) {
            void handleImport();
            return;
        }
        if (step < 5) {
            setStep(current => (current + 1) as WizardStep);
        }
    }, [handleImport, step]);

    const handleBack = useCallback(() => {
        if (step > 1) {
            setStep(current => (current - 1) as WizardStep);
        }
    }, [step]);

    return {
        step,
        file,
        previewing,
        previewError,
        preview,
        mapping,
        domain,
        importing,
        importResult,
        importError,
        canNext,
        setStep,
        setMapping,
        setDomain,
        handleFile,
        handleNext,
        handleBack,
    };
}
