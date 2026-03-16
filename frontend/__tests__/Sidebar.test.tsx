import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import React from "react";
// Since Sidebar could rely on multiple contexts similarly, we provide standard mocks
import Sidebar from "../app/components/Sidebar";

vi.mock("next/navigation", () => ({
  usePathname: () => "/",
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

vi.mock("../app/contexts/BrandingContext", () => ({
  useBranding: () => ({
    branding: { platform_name: "UKIP Default Platform" },
  }),
}));

vi.mock("../app/contexts/AuthContext", () => ({
  useAuth: () => ({ user: { id: "1", role: "admin", username: "admin" } }),
}));

vi.mock("../app/components/SidebarProvider", () => ({
  useSidebar: () => ({ isMobileOpen: true, setMobileOpen: vi.fn() }),
}));

describe("Sidebar Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the branding platform name correctly", () => {
    render(<Sidebar />);
    expect(screen.getByText("UKIP Default Platform")).toBeInTheDocument();
  });

  it("renders main navigation links properly", () => {
    render(<Sidebar />);
    expect(screen.getByText(/Master Data Hub/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Harmonization/i)).toBeInTheDocument();
    expect(screen.getByText(/Semantic RAG/i)).toBeInTheDocument();
  });
});
