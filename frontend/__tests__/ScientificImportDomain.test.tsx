/**
 * Guards the target domain of API-based scientific imports.
 *
 * The regression this replaces: both tabs posted `{ query, limit }` with no
 * `domain`, so the backend default ("science") swallowed every import and there
 * was no way to file records anywhere else from the UI.
 */
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import React from "react";
import ScientificImportPage from "../app/import/scientific/page";
import { LanguageProvider } from "../app/contexts/LanguageContext";

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

vi.mock("@/app/contexts/AssistantContext", () => ({
  useAssistantContextRegistration: () => undefined,
}));

const DOMAINS = [
  {
    id: "science",
    name: "Science & Research",
    description: "Academic papers, publications, patents",
    primary_entity: "Publication",
    icon: "Microscope",
    attributes: [],
  },
  {
    id: "healthcare",
    name: "Healthcare & Clinical",
    description: "Clinical trials, medical devices",
    primary_entity: "Clinical Entity",
    icon: "Activity",
    attributes: [],
  },
];

vi.mock("@/app/contexts/DomainContext", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../app/contexts/DomainContext")>();
  return {
    ...actual,
    useDomain: () => ({
      domains: DOMAINS,
      activeDomainId: "all",
      activeDomain: null,
      setActiveDomainId: vi.fn(),
      isLoading: false,
      refreshDomains: vi.fn(),
    }),
  };
});

import { apiFetch } from "@/lib/api";

function jsonResponse(status: number, body: unknown) {
  return { status, ok: status >= 200 && status < 300, json: async () => body } as Response;
}

function renderPage() {
  localStorage.setItem("app_lang", "en"); // LanguageProvider defaults to "es"
  return render(
    <LanguageProvider>
      <ScientificImportPage />
    </LanguageProvider>
  );
}

/** Body of the most recent POST to the given import endpoint. */
function postedBody(endpoint: string): Record<string, unknown> {
  const call = vi
    .mocked(apiFetch)
    .mock.calls.filter(([path]) => path === endpoint)
    .pop();
  if (!call) throw new Error(`no POST to ${endpoint}`);
  return JSON.parse(String((call[1] as RequestInit).body));
}

beforeEach(() => {
  vi.mocked(apiFetch).mockResolvedValue(
    jsonResponse(202, { job_id: "job-1", status: "queued", record_count: 0 })
  );
});

afterEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

async function openTab(name: RegExp) {
  const user = userEvent.setup();
  await user.click(screen.getByRole("button", { name }));
  return user;
}

describe("PubMed tab", () => {
  test("sends the default science domain when the picker is untouched", async () => {
    renderPage();
    const user = await openTab(/^PubMed$/);

    await user.type(screen.getByPlaceholderText(/systematic review/i), "oncology");
    await user.click(screen.getByRole("button", { name: /Import from PubMed/i }));

    await waitFor(() => expect(postedBody("/import/pubmed").domain).toBe("science"));
  });

  test("sends the domain chosen in the picker", async () => {
    renderPage();
    const user = await openTab(/^PubMed$/);

    await user.type(screen.getByPlaceholderText(/systematic review/i), "oncology");
    await user.selectOptions(screen.getByLabelText(/Target domain/i), "healthcare");
    await user.click(screen.getByRole("button", { name: /Import from PubMed/i }));

    await waitFor(() => expect(postedBody("/import/pubmed").domain).toBe("healthcare"));
  });

  test("lists every registered domain by display name", async () => {
    renderPage();
    await openTab(/^PubMed$/);

    const picker = screen.getByLabelText(/Target domain/i);
    expect(picker).toHaveTextContent("Science & Research");
    expect(picker).toHaveTextContent("Healthcare & Clinical");
  });
});

describe("OpenAlex tab", () => {
  test("sends the domain chosen in the picker", async () => {
    renderPage();
    const user = await openTab(/^OpenAlex$/);

    await user.type(screen.getByPlaceholderText(/knowledge management/i), "bibliometrics");
    await user.selectOptions(screen.getByLabelText(/Target domain/i), "healthcare");
    await user.click(screen.getByRole("button", { name: /Import from OpenAlex/i }));

    await waitFor(() => expect(postedBody("/import/openalex").domain).toBe("healthcare"));
  });

  test("sends the default science domain when the picker is untouched", async () => {
    renderPage();
    const user = await openTab(/^OpenAlex$/);

    await user.type(screen.getByPlaceholderText(/knowledge management/i), "bibliometrics");
    await user.click(screen.getByRole("button", { name: /Import from OpenAlex/i }));

    await waitFor(() => expect(postedBody("/import/openalex").domain).toBe("science"));
  });
});
