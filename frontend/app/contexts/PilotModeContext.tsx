"use client";

import React, { createContext, useCallback, useContext, useSyncExternalStore, type ReactNode } from "react";

interface PilotModeContextType {
    pilotMode: boolean;
    setPilotMode: (value: boolean) => void;
    togglePilotMode: () => void;
}

const PilotModeContext = createContext<PilotModeContextType | undefined>(undefined);

const PILOT_MODE_EVENT = "ukip-pilot-mode-change";
const PILOT_MODE_KEY = "ukip_pilot_mode";

function subscribePilotMode(onStoreChange: () => void): () => void {
    if (typeof window === "undefined") {
        return () => {};
    }
    const handleChange = () => onStoreChange();
    window.addEventListener("storage", handleChange);
    window.addEventListener(PILOT_MODE_EVENT, handleChange);
    return () => {
        window.removeEventListener("storage", handleChange);
        window.removeEventListener(PILOT_MODE_EVENT, handleChange);
    };
}

function getPilotModeSnapshot(): boolean {
    if (typeof window === "undefined") {
        return true;
    }
    const saved = localStorage.getItem(PILOT_MODE_KEY);
    return saved === null ? true : saved === "1";
}

export function PilotModeProvider({ children }: { children: ReactNode }) {
    const pilotMode = useSyncExternalStore<boolean>(
        subscribePilotMode,
        getPilotModeSnapshot,
        () => true,
    );

    const setPilotMode = useCallback((value: boolean) => {
        localStorage.setItem(PILOT_MODE_KEY, value ? "1" : "0");
        window.dispatchEvent(new Event(PILOT_MODE_EVENT));
    }, []);

    const togglePilotMode = useCallback(() => {
        setPilotMode(!getPilotModeSnapshot());
    }, [setPilotMode]);

    return (
        <PilotModeContext.Provider value={{ pilotMode, setPilotMode, togglePilotMode }}>
            {children}
        </PilotModeContext.Provider>
    );
}

export function usePilotMode() {
    const context = useContext(PilotModeContext);
    if (context === undefined) {
        throw new Error("usePilotMode must be used within a PilotModeProvider");
    }
    return context;
}
