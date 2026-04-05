"use client";

type ToastVariant = "success" | "error" | "warning" | "info";

export default function WebhooksTab({
    toast,
}: {
    toast: (msg: string, v?: ToastVariant) => void;
}) {
    void toast;

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
