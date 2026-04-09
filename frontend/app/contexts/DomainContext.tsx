"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { apiFetch } from "@/lib/api";

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

export function DomainProvider({ children }: { children: React.ReactNode }) {
    const [domains, setDomains] = useState<DomainSchema[]>([]);
    const [activeDomainId, setActiveDomainId] = useState<string>("default");
    const [isLoading, setIsLoading] = useState(true);

    const resolveDomainSelection = useCallback((availableDomains: DomainSchema[], currentActiveDomainId: string) => {
        if (availableDomains.length === 0) {
            return currentActiveDomainId || "default";
        }

        const savedDomain = typeof window !== "undefined" ? localStorage.getItem("ukip_active_domain") : null;

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
                        localStorage.setItem("ukip_active_domain", next);
                    }
                    return next;
                });
            }
        } catch {
        } finally {
            setIsLoading(false);
        }
    }, [resolveDomainSelection]);

    useEffect(() => { void fetchDomains(); }, [fetchDomains]);

    const handleSetActiveDomain = (id: string) => {
        setActiveDomainId(id);
        if (typeof window !== "undefined") {
            localStorage.setItem("ukip_active_domain", id);
        }
    };

    const activeDomain = domains.find(d => d.id === activeDomainId) || null;

    return (
        <DomainContext.Provider value={{
            domains,
            activeDomainId,
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
