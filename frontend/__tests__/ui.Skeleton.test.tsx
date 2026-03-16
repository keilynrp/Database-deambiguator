import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import {
  SkeletonText,
  SkeletonAvatar,
  SkeletonBadge,
  SkeletonCard,
  SkeletonCardGrid,
  SkeletonRow,
  SkeletonTableBody,
  SkeletonStatCard,
  SkeletonList,
} from "../app/components/ui/Skeleton";

describe("SkeletonText", () => {
  it("renders with aria-hidden", () => {
    const { container } = render(<SkeletonText />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });

  it("applies custom height class", () => {
    const { container } = render(<SkeletonText height="h-6" />);
    expect(container.firstChild).toHaveClass("h-6");
  });

  it("applies numeric width as inline style", () => {
    const { container } = render(<SkeletonText width={120} />);
    expect((container.firstChild as HTMLElement).style.width).toBe("120px");
  });
});

describe("SkeletonAvatar", () => {
  it("renders with aria-hidden and rounded-full", () => {
    const { container } = render(<SkeletonAvatar />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
    expect(container.firstChild).toHaveClass("rounded-full");
  });
});

describe("SkeletonBadge", () => {
  it("renders with aria-hidden", () => {
    const { container } = render(<SkeletonBadge />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });
});

describe("SkeletonCard", () => {
  it("renders with aria-hidden", () => {
    const { container } = render(<SkeletonCard />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });

  it("renders correct number of line shimmer divs (1 heading + N body)", () => {
    const { container } = render(<SkeletonCard lines={3} />);
    // heading + 3 body lines = 4 animated divs total
    const animated = container.querySelectorAll(".animate-pulse");
    expect(animated.length).toBe(4);
  });
});

describe("SkeletonCardGrid", () => {
  it("renders the requested number of cards", () => {
    const { container } = render(<SkeletonCardGrid count={3} />);
    // Each card wrapper has aria-hidden; count direct children of grid
    const grid = container.firstChild as HTMLElement;
    expect(grid.children.length).toBe(3);
  });
});

describe("SkeletonRow", () => {
  it("renders correct number of <td> cells", () => {
    const { container } = render(
      <table><tbody><SkeletonRow cols={4} /></tbody></table>
    );
    expect(container.querySelectorAll("td").length).toBe(4);
  });

  it("has aria-hidden on the row", () => {
    const { container } = render(
      <table><tbody><SkeletonRow /></tbody></table>
    );
    expect(container.querySelector("tr")).toHaveAttribute("aria-hidden", "true");
  });
});

describe("SkeletonTableBody", () => {
  it("renders the correct number of rows", () => {
    const { container } = render(
      <table><tbody><SkeletonTableBody rows={5} cols={3} /></tbody></table>
    );
    expect(container.querySelectorAll("tr").length).toBe(5);
  });
});

describe("SkeletonStatCard", () => {
  it("renders with aria-hidden", () => {
    const { container } = render(<SkeletonStatCard />);
    expect(container.firstChild).toHaveAttribute("aria-hidden", "true");
  });
});

describe("SkeletonList", () => {
  it("renders the correct number of list items", () => {
    const { container } = render(<SkeletonList rows={4} />);
    // Each item has a flex wrapper; count them via the border-b class
    const items = container.querySelectorAll(".border-b");
    expect(items.length).toBe(4);
  });
});
