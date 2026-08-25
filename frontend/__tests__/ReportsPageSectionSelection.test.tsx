/**
 * Regression for the P2 review finding on PR #314 (issue #268 follow-up):
 * `loadSections()` reruns whenever `language` changes (e.g. a cross-tab
 * language switch dispatches `ukip-language-change`), and its success path
 * used to call `setSelected(new Set(data.map((s) => s.id)))` unconditionally
 * — silently discarding whatever the user had manually selected. Select-all
 * must only happen on the page's first load; a later refresh (same section
 * IDs, freshly translated labels) must leave an existing selection alone.
 */
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import React from "react";
import ReportsPage from "../app/reports/page";
import { LanguageProvider } from "../app/contexts/LanguageContext";

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

vi.mock("@/app/contexts/AssistantContext", () => ({
  useAssistantContextRegistration: () => undefined,
}));

vi.mock("@/app/contexts/DomainContext", () => ({
  useDomain: () => ({
    domains: [],
    activeDomainId: "all",
    activeDomain: null,
    setActiveDomainId: vi.fn(),
    isLoading: false,
    refreshDomains: vi.fn(),
  }),
}));

vi.mock("next/navigation", () => ({
  useSearchParams: () => new URLSearchParams(""),
}));

import { apiFetch } from "@/lib/api";

const SECTIONS_EN = [
  { id: "entity_stats", label: "Entity Statistics", formats: { html: true } },
  { id: "top_concepts", label: "Top Concepts", formats: { html: true } },
];
const SECTIONS_ES = [
  { id: "entity_stats", label: "Estadísticas de Entidades", formats: { html: true } },
  { id: "top_concepts", label: "Principales Conceptos", formats: { html: true } },
];

function jsonResponse(status: number, body: unknown) {
  return { status, ok: status >= 200 && status < 300, json: async () => body } as Response;
}

function mockApi() {
  vi.mocked(apiFetch).mockImplementation(async (path: string) => {
    if (path.startsWith("/reports/sections")) {
      const language = new URL(path, "http://localhost").searchParams.get("language");
      return jsonResponse(200, language === "es" ? SECTIONS_ES : SECTIONS_EN);
    }
    if (path.startsWith("/analytics/benchmarks/profiles")) {
      return jsonResponse(200, []);
    }
    return jsonResponse(200, {});
  });
}

function renderPage() {
  localStorage.setItem("app_lang", "en");
  return render(
    <LanguageProvider>
      <ReportsPage />
    </LanguageProvider>
  );
}

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

test("a language change refreshes section labels without resetting an existing selection", async () => {
  mockApi();
  renderPage();

  await waitFor(() => expect(screen.getByText("Entity Statistics")).toBeInTheDocument());
  // Initial load selects every returned section.
  await waitFor(() =>
    expect(screen.getByText("2 of 2 selected")).toBeInTheDocument()
  );

  // Deselect one section — a manual choice that must survive a relabel.
  // The picker renders each section as a <button>; the same label also
  // appears in the read-only "Included Sections" preview list below it, so
  // scope the click to the toggle button specifically.
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name: /Top Concepts/ }));
  await waitFor(() =>
    expect(screen.getByText("1 of 2 selected")).toBeInTheDocument()
  );

  // Cross-tab language switch: localStorage changes, `ukip-language-change` fires.
  act(() => {
    localStorage.setItem("app_lang", "es");
    window.dispatchEvent(new Event("ukip-language-change"));
  });

  // Labels refresh to Spanish (each also appears in the read-only "Included
  // Sections" preview list, so assert presence rather than a unique match)...
  await waitFor(() => expect(screen.getAllByText("Estadísticas de Entidades").length).toBeGreaterThan(0));
  expect(screen.getAllByText("Principales Conceptos").length).toBeGreaterThan(0);
  expect(screen.queryAllByText("Entity Statistics")).toHaveLength(0);

  // ...but the manual deselection is not clobbered by the refresh's select-all.
  expect(screen.getByText("1 de 2 seleccionadas")).toBeInTheDocument();
});
