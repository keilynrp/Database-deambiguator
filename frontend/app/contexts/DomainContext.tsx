"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";

const DOMAIN_STORAGE_KEY = "ukip_active_domain";

export interface DomainAttribute {
    name: string;
    type: string;
    label: string;
    required: boolean;
    is_core: boolean;
}

export interface DomainSchema {
    id: string;
    name: string;
    description: string;
    primary_entity: string;
    icon: string;
    attributes: DomainAttribute[];
}

interface DomainContextType {
    domains: DomainSchema[];
    activeDomainId: string;
    activeDomain: DomainSchema | null;
    setActiveDomainId: (id: string) => void;
    isLoading: boolean;
    refreshDomains: () => Promise<void>;
}

const DomainContext = createContext<DomainContextType | undefined>(undefined);

function readStoredDomain(): string | null {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem(DOMAIN_STORAGE_KEY);
}

export function DomainProvider({ children }: { children: React.ReactNode }) {
    const [domains, setDomains] = useState<DomainSchema[]>([]);
    const [activeDomainId, setActiveDomainId] = useState<string>(() => readStoredDomain() || "default");
    const [isLoading, setIsLoading] = useState(true);

    const resolveDomainSelection = useCallback((availableDomains: DomainSchema[], currentActiveDomainId: string) => {
        if (availableDomains.length === 0) {
            return currentActiveDomainId || "default";
        }

        const savedDomain = readStoredDomain();

        if (currentActiveDomainId && availableDomains.some((d) => d.id === currentActiveDomainId)) {
            return currentActiveDomainId;
        }

        if (savedDomain && availableDomains.some((d) => d.id === savedDomain)) {
            return savedDomain;
        }

        const defaultDomain = availableDomains.find((d) => d.id === "default");
        return defaultDomain ? defaultDomain.id : availableDomains[0].id;
    }, []);

    const fetchDomains = useCallback(async () => {
        try {
            const res = await apiFetch("/domains");
            if (res.ok) {
                const data = await res.json();
                setDomains(data);

                setActiveDomainId((prev) => {
                    const next = resolveDomainSelection(data, prev);
                    if (typeof window !== "undefined") {
                        window.localStorage.setItem(DOMAIN_STORAGE_KEY, next);
                    }
                    return next;
                });
            }
        } catch {
        } finally {
            setIsLoading(false);
        }
    }, [resolveDomainSelection]);

    useEffect(() => {
        const storedDomain = readStoredDomain();
        if (storedDomain) {
            setActiveDomainId((prev) => prev || storedDomain);
        }
    }, []);

    useEffect(() => { void fetchDomains(); }, [fetchDomains]);

    const handleSetActiveDomain = (id: string) => {
        if (!id) return;
        setActiveDomainId(id);
        if (typeof window !== "undefined") {
            window.localStorage.setItem(DOMAIN_STORAGE_KEY, id);
        }
    };

    const activeDomain =
        domains.find((d) => d.id === activeDomainId)
        || domains.find((d) => d.id === "default")
        || domains[0]
        || null;
    const resolvedActiveDomainId = activeDomain?.id || activeDomainId || "default";

    return (
        <DomainContext.Provider value={{
            domains,
            activeDomainId: resolvedActiveDomainId,
            activeDomain,
            setActiveDomainId: handleSetActiveDomain,
            isLoading,
            refreshDomains: fetchDomains,
        }}>
            {children}
        </DomainContext.Provider>
    );
}

export function useDomain() {
    const context = useContext(DomainContext);
    if (!context) {
        throw new Error("useDomain must be used within a DomainProvider");
    }
    return context;
}
