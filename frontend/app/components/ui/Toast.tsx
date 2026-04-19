"use client";

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from "react";
import { createPortal } from "react-dom";
import { useLanguage } from "../../contexts/LanguageContext";

export type ToastVariant = "success" | "error" | "warning" | "info";

interface ToastItem {
    id: number;
    message: string;
    variant: ToastVariant;
}

interface ToastContextValue {
    toast: (message: string, variant?: ToastVariant) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export function useToast() {
    return useContext(ToastContext);
}

const STYLES: Record<ToastVariant, string> = {
    success: "border-green-200 bg-green-50 text-green-800 dark:border-green-700/50 dark:bg-green-900/30 dark:text-green-300",
    error:   "border-red-200 bg-red-50 text-red-800 dark:border-red-700/50 dark:bg-red-900/30 dark:text-red-300",
    warning: "border-yellow-200 bg-yellow-50 text-yellow-800 dark:border-yellow-700/50 dark:bg-yellow-900/30 dark:text-yellow-300",
    info:    "border-blue-200 bg-blue-50 text-blue-800 dark:border-blue-700/50 dark:bg-blue-900/30 dark:text-blue-300",
};

const ICON_STYLES: Record<ToastVariant, string> = {
    success: "bg-green-100 text-green-600 dark:bg-green-800 dark:text-green-300",
    error:   "bg-red-100 text-red-600 dark:bg-red-800 dark:text-red-300",
    warning: "bg-yellow-100 text-yellow-600 dark:bg-yellow-800 dark:text-yellow-300",
    info:    "bg-blue-100 text-blue-600 dark:bg-blue-800 dark:text-blue-300",
};

const ICONS: Record<ToastVariant, string> = {
    success: "✓",
    error:   "✕",
    warning: "⚠",
    info:    "i",
};
const PROGRESS_STYLES: Record<ToastVariant, string> = {
    success: "bg-green-500/70 dark:bg-green-400/70",
    error:   "bg-red-500/70 dark:bg-red-400/70",
    warning: "bg-yellow-500/70 dark:bg-yellow-400/70",
    info:    "bg-blue-500/70 dark:bg-blue-400/70",
};

let nextId = 0;
const DURATION = 4500;

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<ToastItem[]>([]);
    const [mounted, setMounted] = useState(false);
    const { t } = useLanguage();

    useEffect(() => {
        setMounted(true);
    }, []);

    const toast = useCallback((message: string, variant: ToastVariant = "info") => {
        const id = ++nextId;
        setToasts(prev => [...prev, { id, message, variant }]);
        setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), DURATION);
    }, []);

    const dismiss = useCallback((id: number) => {
        setToasts(prev => prev.filter(t => t.id !== id));
    }, []);

    const toastContainer = (
        <div
            aria-live="polite"
            aria-label={t("common.toast.region")}
            className="pointer-events-none fixed inset-x-4 bottom-5 z-[200] flex flex-col gap-2 sm:inset-x-auto sm:right-5 sm:w-auto"
        >
            {toasts.map((item) => (
                <div
                    key={item.id}
                    className={`pointer-events-auto relative overflow-hidden rounded-xl border px-4 py-3 shadow-lg toast-enter ${STYLES[item.variant]}`}
                    style={{ minWidth: 280, maxWidth: 420 }}
                >
                    <div
                        className={`absolute inset-x-0 bottom-0 h-1 origin-left animate-[toast-progress_4.5s_linear_forwards] ${PROGRESS_STYLES[item.variant]}`}
                    />
                    <div className="flex items-start gap-3">
                        <span className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${ICON_STYLES[item.variant]}`}>
                            {ICONS[item.variant]}
                        </span>
                        <div className="min-w-0 flex-1">
                            <p className="text-xs font-semibold uppercase tracking-[0.14em] opacity-80">
                                {t(`common.toast.${item.variant}`)}
                            </p>
                            <p className="mt-1 text-sm font-medium leading-snug break-words">{item.message}</p>
                        </div>
                        <button
                            onClick={() => dismiss(item.id)}
                            className="shrink-0 rounded p-0.5 opacity-50 transition-opacity hover:opacity-100"
                            aria-label={t("common.dismiss")}
                        >
                            <svg className="h-3.5 w-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <ToastContext.Provider value={{ toast }}>
            {children}
            {mounted && createPortal(toastContainer, document.body)}
        </ToastContext.Provider>
    );
}
