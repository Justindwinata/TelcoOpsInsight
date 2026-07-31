import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("App", () => {
  it("renders the NOC dashboard shell", () => {
    render(<App />);

    expect(screen.getByText("TelcoOps Insight")).toBeInTheDocument();
    expect(screen.getAllByText("Executive Overview").length).toBeGreaterThan(0);
    expect(screen.getByText("Synthetic 2026 Dataset")).toBeInTheDocument();
  });

  it("switches dashboard sections from the sidebar", () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Recommendations" }));

    expect(screen.getAllByText("Recommendations").length).toBeGreaterThan(0);
    expect(screen.getByText("Loading recommendations...")).toBeInTheDocument();
  });
});
