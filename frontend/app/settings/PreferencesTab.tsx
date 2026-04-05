"use client";

import type { Language } from "../i18n/translations";

type Theme = "light" | "dark";

export default function PreferencesTab({
    language,
    setLanguage,
    theme,
    setTheme,
    t,
}: {
    language: Language;
    setLanguage: (language: Language) => void;
    theme: Theme;
    setTheme: (theme: Theme) => void;
    t: (key: string) => string;
}) {
    return (
        <div className="space-y-4">
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
                                <span className="text-lg">{lang === "en" ? "US" : "ES"}</span>
                                {lang === "en" ? "English" : "Español"}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-800 dark:bg-gray-900">
                <div className="flex items-start justify-between">
                    <div>
                        <h3 className="text-base font-medium text-gray-900 dark:text-white">{t("settings.theme")}</h3>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">{t("settings.theme.desc")}</p>
                    </div>
                    <div className="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-1 dark:border-gray-700 dark:bg-gray-800">
                        <button
                            onClick={() => setTheme("light")}
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
                            onClick={() => setTheme("dark")}
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
