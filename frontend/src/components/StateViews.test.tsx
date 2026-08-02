import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";

describe("State Views", () => {
  it("renders loading state with spinner", () => {
    render(<LoadingState label="Test loading" />);
    expect(screen.getByText("Test loading...")).toBeTruthy();
  });

  it("renders error state with message", () => {
    render(<ErrorState message="Something went wrong" />);
    expect(screen.getByText("Something went wrong")).toBeTruthy();
    expect(screen.getByText("Error")).toBeTruthy();
  });

  it("renders empty state with default message", () => {
    render(<EmptyState />);
    expect(screen.getByText("No records available for the selected view.")).toBeTruthy();
  });

  it("renders empty state with custom message", () => {
    render(<EmptyState message="No data" />);
    expect(screen.getByText("No data")).toBeTruthy();
  });
});
