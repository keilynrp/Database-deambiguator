import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import React from "react";
import Sidebar from "../app/components/Sidebar";
import { LanguageProvider } from "../app/contexts/LanguageContext";

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

function renderSidebar() {
  return render(
    <LanguageProvider>
      <Sidebar />
    </LanguageProvider>
  );
}

describe("Sidebar Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.setItem("app_lang", "en");
  });

  it("renders the branding platform name correctly", async () => {
    renderSidebar();
    expect(await screen.findByText("UKIP Default Platform")).toBeInTheDocument();
  });

  it("renders main navigation links properly", async () => {
    renderSidebar();
    expect(await screen.findByText(/Knowledge Explorer/i)).toBeInTheDocument();
    expect(screen.getByText(/Harmonization/i)).toBeInTheDocument();
    expect(screen.getByText(/Semantic AI/i)).toBeInTheDocument();
  });
});
