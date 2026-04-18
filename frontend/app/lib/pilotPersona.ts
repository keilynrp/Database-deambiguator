"use client";

export type PilotPersonaId = "research" | "library" | "leadership";
export type StakeholderProfile = "leadership" | "research_office" | "library" | "innovation";

export const PILOT_PERSONA_STORAGE_KEY = "ukip_persona_v1";

export function getStoredPilotPersona(): PilotPersonaId | null {
  if (typeof window === "undefined") return null;
  const stored = window.localStorage.getItem(PILOT_PERSONA_STORAGE_KEY);
  if (stored === "research" || stored === "library" || stored === "leadership") {
    return stored;
  }
  return null;
}

export function setStoredPilotPersona(persona: PilotPersonaId) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(PILOT_PERSONA_STORAGE_KEY, persona);
}

export function pilotPersonaToStakeholder(persona: PilotPersonaId | null): StakeholderProfile {
  switch (persona) {
    case "research":
      return "research_office";
    case "library":
      return "library";
    case "leadership":
    default:
      return "leadership";
  }
}
