import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
import DisambiguationTool from "../app/components/DisambiguationTool";

vi.mock("../app/components/ui/Toast", () => ({
  useToast: () => ({ toast: vi.fn() }),
}));

vi.mock("@/lib/api", () => ({
  apiFetch: vi.fn().mockResolvedValue({
    ok: true,
    json: () => Promise.resolve({ total_groups: 0, items: [] })
  }),
}));

describe("DisambiguationTool Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders correctly with controls based on context", () => {
    render(<DisambiguationTool />);
    expect(screen.getByText(/Target Similarity Threshold/i)).toBeInTheDocument();
    expect(screen.getByText(/Detect Duplicates/i)).toBeInTheDocument();
  });

  it("presents available clustering algorithms", () => {
    render(<DisambiguationTool />);
    expect(screen.getByRole("combobox", { name: /clustering algorithm/i })).toBeInTheDocument();
  });
});
