import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, act } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import EntityTable from "../app/components/EntityTable";

// ── Mock all external dependencies ────────────────────────────────────────

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

vi.mock("../app/contexts/DomainContext", () => ({
  useDomain: () => ({
    // null → component falls back to "Primary Label" column, showing primary_label text
    activeDomain: null,
    activeDomainId: "default",
  }),
}));

vi.mock("../app/components/ui", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../app/components/ui")>();
  return {
    ...actual,
    useToast: () => ({ toast: vi.fn() }),
  };
});

// FacetPanel is a heavy dependency — stub it out
vi.mock("../app/components/FacetPanel", () => ({
  default: ({ onFacetChange }: { onFacetChange: (f: string, v: string | null) => void }) => (
    <div data-testid="facet-panel">FacetPanel</div>
  ),
}));

// MonteCarloChart stub
vi.mock("../app/components/MonteCarloChart", () => ({
  default: () => <div>MonteCarloChart</div>,
}));

// Stub window.confirm
vi.stubGlobal("confirm", vi.fn(() => true));

// Stub URL.createObjectURL for CSV export
vi.stubGlobal("URL", {
  createObjectURL: vi.fn(() => "blob:url"),
  revokeObjectURL: vi.fn(),
});

import { apiFetch } from "@/lib/api";
const mockApiFetch = apiFetch as ReturnType<typeof vi.fn>;

// ── Fixtures ───────────────────────────────────────────────────────────────

const MOCK_ENTITIES = [
  {
    id: 1,
    primary_label: "Einstein",
    secondary_label: "Albert Einstein",
    canonical_id: "Q937",
    entity_type: "person",
    domain: "default",
    validation_status: "confirmed",
    enrichment_status: "completed",
    enrichment_citation_count: 42,
    source: "user",
    attributes_json: null,
    normalized_json: null,
    quality_score: 0.9,
  },
  {
    id: 2,
    primary_label: "CERN",
    secondary_label: null,
    canonical_id: null,
    entity_type: "organization",
    domain: "default",
    validation_status: "pending",
    enrichment_status: "none",
    enrichment_citation_count: null,
    source: "user",
    attributes_json: null,
    normalized_json: null,
    quality_score: 0.4,
  },
];

function successResponse(data: unknown, headers?: Record<string, string>) {
  return {
    ok: true,
    headers: {
      get: (key: string) => (headers ?? {})[key] ?? null,
    },
    json: async () => data,
  };
}

// ── Tests ──────────────────────────────────────────────────────────────────

beforeEach(() => {
  mockApiFetch.mockReset();
});

describe("EntityTable", () => {
  it("shows skeleton loader while fetching", () => {
    // Never resolve — stays loading
    mockApiFetch.mockReturnValue(new Promise(() => {}));
    render(<EntityTable />);
    expect(document.querySelectorAll("[aria-hidden='true']").length).toBeGreaterThan(0);
  });

  it("renders entity rows after fetch", async () => {
    mockApiFetch.mockResolvedValue(
      successResponse(MOCK_ENTITIES, { "X-Total-Count": "2" })
    );
    render(<EntityTable />);
    await waitFor(() => {
      expect(screen.getByText("Einstein")).toBeInTheDocument();
      expect(screen.getByText("CERN")).toBeInTheDocument();
    });
  });

  it("shows ErrorBanner on fetch failure", async () => {
    mockApiFetch.mockResolvedValue({ ok: false, headers: { get: () => null }, json: async () => ({}) });
    render(<EntityTable />);
    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
    });
  });

  it("displays quality score bar for entities with score", async () => {
    mockApiFetch.mockResolvedValue(
      successResponse(MOCK_ENTITIES, { "X-Total-Count": "2" })
    );
    render(<EntityTable />);
    await waitFor(() => {
      // Einstein has score 0.9 → 90%
      expect(screen.getByText("90%")).toBeInTheDocument();
    });
  });

  it("renders search input", async () => {
    mockApiFetch.mockResolvedValue(successResponse([], { "X-Total-Count": "0" }));
    render(<EntityTable />);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Search entities...")).toBeInTheDocument();
    });
  });

  it("typing in search triggers a new fetch", async () => {
    mockApiFetch.mockResolvedValue(successResponse(MOCK_ENTITIES, { "X-Total-Count": "2" }));
    render(<EntityTable />);
    await waitFor(() => screen.getByPlaceholderText("Search entities..."));

    await act(async () => {
      await userEvent.type(screen.getByPlaceholderText("Search entities..."), "Ein");
      // Wait for the 500ms debounce + fetch
      await new Promise(r => setTimeout(r, 600));
    });

    // At least 2 calls: initial load + debounced search
    expect(mockApiFetch.mock.calls.length).toBeGreaterThanOrEqual(2);
  });

  it("shows FacetPanel", async () => {
    mockApiFetch.mockResolvedValue(successResponse([], { "X-Total-Count": "0" }));
    render(<EntityTable />);
    await waitFor(() => {
      expect(screen.getByTestId("facet-panel")).toBeInTheDocument();
    });
  });

  it("shows empty state message when no entities match", async () => {
    mockApiFetch.mockResolvedValue(successResponse([], { "X-Total-Count": "0" }));
    render(<EntityTable />);
    await waitFor(() => {
      expect(screen.getByText(/no entities/i)).toBeInTheDocument();
    });
  });
});
