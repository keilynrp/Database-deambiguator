"use client";

import { PageHeader } from "../components/ui";
import {
    STEPS,
    StepBar,
    StepDomain,
    StepImport,
    StepMapping,
    StepUpload,
    StepValidate,
} from "./importWizardParts";
import useImportWizardController from "./useImportWizardController";

export default function ImportWizardPage() {
    const {
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
    } = useImportWizardController();

    return (
        <div className="space-y-6">
            <PageHeader
                breadcrumbs={[
                    { label: "Home", href: "/" },
                    { label: "Import Wizard" },
                ]}
                title="Bulk Import Wizard"
                description="Import CSV, Excel, BibTeX, RIS, JSON, XML, or Parquet files with guided field mapping and domain selection."
            />

            <div className="flex justify-center py-2">
                <StepBar current={step} />
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <h2 className="mb-5 text-sm font-bold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                    Step {step} - {STEPS[step - 1].label}
                </h2>

                {step === 1 && <StepUpload file={file} onFile={handleFile} />}

                {step === 2 && (
                    previewing ? (
                        <div className="flex flex-col items-center gap-3 py-12">
                            <svg className="h-7 w-7 animate-spin text-indigo-600" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            <p className="text-sm text-gray-500">Parsing file and detecting columns...</p>
                        </div>
                    ) : previewError ? (
                        <div className="rounded-xl border border-red-200 bg-red-50 p-5 dark:border-red-500/30 dark:bg-red-500/5">
                            <p className="text-sm font-medium text-red-700 dark:text-red-400">{previewError}</p>
                            <button onClick={() => setStep(1)} className="mt-2 text-xs text-red-600 underline dark:text-red-400">
                                Back and try another file
                            </button>
                        </div>
                    ) : preview ? (
                        <StepMapping preview={preview} mapping={mapping} onMappingChange={setMapping} />
                    ) : null
                )}

                {step === 3 && <StepDomain selected={domain} onSelect={setDomain} />}

                {step === 4 && preview && <StepValidate preview={preview} mapping={mapping} domain={domain} />}

                {step === 5 && <StepImport result={importResult} importing={importing} error={importError} />}
            </div>

            {step < 5 && (
                <div className="flex items-center justify-between">
                    <button
                        onClick={handleBack}
                        disabled={step === 1}
                        className="flex items-center gap-2 rounded-lg border border-gray-200 px-4 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 disabled:opacity-40 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-800"
                    >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back
                    </button>

                    <button
                        onClick={handleNext}
                        disabled={!canNext[step]}
                        className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700 disabled:opacity-40"
                    >
                        {step === 4 ? "Import Now" : "Next"}
                        {step < 4 && (
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                            </svg>
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}
