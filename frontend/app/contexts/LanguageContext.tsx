"use client";

import React, { createContext, useContext, useCallback, useSyncExternalStore, ReactNode } from "react";
import { translations, Language } from "../i18n/translations";

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: (key: string, params?: Record<string, string | number>) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

const LANGUAGE_EVENT = "ukip-language-change";

function subscribeLanguage(onStoreChange: () => void): () => void {
    if (typeof window === "undefined") {
        return () => {};
    }
    const handleChange = () => onStoreChange();
    window.addEventListener("storage", handleChange);
    window.addEventListener(LANGUAGE_EVENT, handleChange);
    return () => {
        window.removeEventListener("storage", handleChange);
        window.removeEventListener(LANGUAGE_EVENT, handleChange);
    };
}

function getLanguageSnapshot(): Language {
    if (typeof window === "undefined") {
        return "es";
    }
    const saved = localStorage.getItem("app_lang");
    return saved === "en" || saved === "es" ? saved : "es";
}

export function LanguageProvider({ children }: { children: ReactNode }) {
    const language = useSyncExternalStore(subscribeLanguage, getLanguageSnapshot, () => "es");

    const changeLanguage = useCallback((lang: Language) => {
        localStorage.setItem("app_lang", lang);
        window.dispatchEvent(new Event(LANGUAGE_EVENT));
    }, []);

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
