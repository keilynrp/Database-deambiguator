import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import EmptyState from "../app/components/ui/EmptyState";

describe("EmptyState", () => {
  it("renders title", () => {
    render(<EmptyState title="No results" />);
    expect(screen.getByText("No results")).toBeInTheDocument();
  });

  it("renders description when provided", () => {
    render(<EmptyState title="Empty" description="Try uploading data first" />);
    expect(screen.getByText("Try uploading data first")).toBeInTheDocument();
  });

  it("does not render description when omitted", () => {
    render(<EmptyState title="Empty" />);
    expect(screen.queryByText(/Try uploading/)).not.toBeInTheDocument();
  });

  it("renders a link CTA with href", () => {
    render(
      <EmptyState
        title="Empty"
        cta={{ label: "Import data", href: "/import" }}
      />
    );
    const link = screen.getByRole("link", { name: "Import data" });
    expect(link).toHaveAttribute("href", "/import");
  });

  it("renders a button CTA with onClick", () => {
    const onClick = vi.fn();
    render(
      <EmptyState
        title="Empty"
        cta={{ label: "Clear filter", onClick }}
      />
    );
    const btn = screen.getByRole("button", { name: "Clear filter" });
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("renders multiple CTAs", () => {
    render(
      <EmptyState
        title="Empty"
        cta={[
          { label: "Primary", href: "/primary" },
          { label: "Secondary", href: "/secondary", variant: "secondary" },
        ]}
      />
    );
    expect(screen.getByRole("link", { name: "Primary" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Secondary" })).toBeInTheDocument();
  });

  it("applies page size padding class", () => {
    const { container } = render(<EmptyState title="Empty" size="page" />);
    expect(container.firstChild).toHaveClass("py-24");
  });

  it("applies compact size padding class", () => {
    const { container } = render(<EmptyState title="Empty" size="compact" />);
    expect(container.firstChild).toHaveClass("py-8");
  });

  it("renders preset icon for known key", () => {
    const { container } = render(<EmptyState title="Empty" icon="bell" />);
    expect(container.querySelector("svg")).toBeInTheDocument();
  });
});
