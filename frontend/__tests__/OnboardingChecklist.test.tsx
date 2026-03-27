import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";

vi.mock("../lib/api", () => ({
  apiFetch: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

import OnboardingChecklist from "../app/components/OnboardingChecklist";
import { apiFetch } from "../lib/api";

const mockApiFetch = apiFetch as ReturnType<typeof vi.fn>;

function successResponse(data: unknown) {
  return {
    ok: true,
    json: async () => data,
  };
}

const BASE_STATUS = {
  completed: 0,
  total: 5,
  percent: 0,
  all_done: false,
  commercial_mvp: {
    key: "research_intelligence",
    label: "Research Intelligence",
    summary: "Initial commercial focus for research portfolio onboarding.",
    ideal_customer: "Research office or library analytics team",
    initial_dataset: "CSV or RIS",
    time_to_first_value: "30-60 minutes",
    primary_outcomes: [
      "Consolidate publication records",
      "Enrich authors and affiliations",
      "Review portfolio KPIs",
    ],
  },
  journey: [
    {
      key: "load_portfolio",
      label: "Load a publication portfolio",
      description: "Bring your initial dataset.",
      href: "/import-export",
    },
    {
      key: "enrich_and_resolve",
      label: "Enrich authors and affiliations",
      description: "Improve metadata quality.",
      href: "/authority",
    },
  ],
  next_recommended_step: {
    key: "import_data",
    label: "Import publication data",
    description: "Upload publications and authors.",
    href: "/import-export",
    reason: "Fastest path to first value.",
  },
  steps: [
    {
      key: "import_data",
      label: "Import publication data",
      description: "Upload publications and authors.",
      href: "/import-export",
      icon: "upload",
      completed: false,
    },
    {
      key: "enrich_entity",
      label: "Enrich a research record",
      description: "Add metadata from academic sources.",
      href: "/",
      icon: "sparkles",
      completed: false,
    },
  ],
};

beforeEach(() => {
  localStorage.clear();
  mockApiFetch.mockReset();
});

describe("OnboardingChecklist", () => {
  it("renders the commercial MVP context and recommended next step", async () => {
    mockApiFetch.mockResolvedValue(successResponse(BASE_STATUS));

    render(<OnboardingChecklist token="token" />);

    await waitFor(() => {
      expect(screen.getByText("Research Intelligence")).toBeInTheDocument();
    });

    expect(screen.getByText("Initial commercial focus")).toBeInTheDocument();
    expect(screen.getByText("Fastest path to first value.")).toBeInTheDocument();
    expect(screen.getByText("Recommended now")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Go now" })).toHaveAttribute("href", "/import-export");
  });

  it("stays hidden when onboarding is already complete", async () => {
    mockApiFetch.mockResolvedValue(
      successResponse({
        ...BASE_STATUS,
        completed: 5,
        percent: 100,
        all_done: true,
        next_recommended_step: null,
      })
    );

    const { container } = render(<OnboardingChecklist token="token" />);

    await waitFor(() => {
      expect(mockApiFetch).toHaveBeenCalledTimes(1);
    });

    expect(container).toBeEmptyDOMElement();
  });
});
