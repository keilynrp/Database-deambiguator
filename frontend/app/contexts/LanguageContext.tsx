"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { translations, Language } from "../i18n/translations";

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
    const [language, setLanguage] = useState<Language>(() => {
        if (typeof window !== "undefined") {
            const saved = localStorage.getItem("app_lang");
            if (saved === "en" || saved === "es") {
                return saved;
            }
        }
        return "es";
    });
    const changeLanguage = (lang: Language) => {
        setLanguage(lang);
        localStorage.setItem("app_lang", lang);
    };

    const t = (key: string, params?: Record<string, string | number>): string => {
        const dict = translations[language] as Record<string, string>;
        const template = dict[key] || key;
        if (!params) return template;

        return Object.entries(params).reduce((message, [paramKey, value]) => {
            return message.replaceAll(`{${paramKey}}`, String(value));
        }, template);
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage: changeLanguage, t }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error("useLanguage must be used within a LanguageProvider");
    }
    return context;
}
