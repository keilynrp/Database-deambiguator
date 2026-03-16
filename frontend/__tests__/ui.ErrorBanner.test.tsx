import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import ErrorBanner from "../app/components/ui/ErrorBanner";

describe("ErrorBanner", () => {
  it("renders message text", () => {
    render(<ErrorBanner message="Something went wrong" />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("has role=alert for accessibility", () => {
    render(<ErrorBanner message="Error" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("renders detail when provided (card variant)", () => {
    render(<ErrorBanner message="Upload failed" detail="413 Request Too Large" />);
    expect(screen.getByText("413 Request Too Large")).toBeInTheDocument();
  });

  it("renders Retry button when onRetry provided (card variant)", () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Error" onRetry={onRetry} />);
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("does not render Retry button when onRetry omitted", () => {
    render(<ErrorBanner message="Error" />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("inline variant renders Retry label correctly", () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Error" onRetry={onRetry} variant="inline" />);
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /retry/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("row variant renders try again button", () => {
    const onRetry = vi.fn();
    render(<ErrorBanner message="Load error" onRetry={onRetry} variant="row" />);
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("inline variant has role=alert", () => {
    render(<ErrorBanner message="Oops" variant="inline" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
