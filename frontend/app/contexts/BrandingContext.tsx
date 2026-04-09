"use client";

import React, { createContext, useContext, useState, useEffect, useCallback } from "react";

export interface BrandingSettings {
  platform_name: string;
  logo_url: string;
  favicon_url: string;
  accent_color: string;
  footer_text: string;
}

const DEFAULTS: BrandingSettings = {
  platform_name: "UKIP",
  logo_url: "",
  favicon_url: "",
  accent_color: "#6366f1",
  footer_text: "Universal Knowledge Intelligence Platform",
};

interface BrandingContextType {
  branding: BrandingSettings;
  refreshBranding: () => Promise<void>;
}

const BrandingContext = createContext<BrandingContextType | undefined>(undefined);

export function BrandingProvider({ children }: { children: React.ReactNode }) {
  const [branding, setBranding] = useState<BrandingSettings>(DEFAULTS);

  const fetchBranding = useCallback(async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const res = await fetch(`${apiUrl}/branding/settings`);
      if (res.ok) {
        const data = await res.json();
        return { ...DEFAULTS, ...data };
      }
    } catch {
      return null;
    }
    return null;
  }, []);

  const refreshBranding = useCallback(async () => {
    const nextBranding = await fetchBranding();
    if (nextBranding) {
      setBranding(nextBranding);
    }
  }, [fetchBranding]);

  useEffect(() => {
    let active = true;
    void fetchBranding().then((nextBranding) => {
      if (active && nextBranding) {
        setBranding(nextBranding);
      }
    });
    return () => {
      active = false;
    };
  }, [fetchBranding]);

  return (
    <BrandingContext.Provider value={{ branding, refreshBranding }}>
      {children}
    </BrandingContext.Provider>
  );
}

export function useBranding(): BrandingContextType {
  const ctx = useContext(BrandingContext);
  if (!ctx) throw new Error("useBranding must be used within a BrandingProvider");
  return ctx;
}
