import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { FilterPanel } from "./FilterPanel";
import { FilterProvider } from "../filters/FilterContext";

describe("FilterPanel", () => {
  afterEach(() => {
    localStorage.clear();
  });

  it("shows active filter summary and reset behavior", () => {
    render(
      <FilterProvider>
        <FilterPanel />
      </FilterProvider>
    );

    fireEvent.change(screen.getByLabelText("Region"), { target: { value: "Jakarta" } });

    expect(screen.getByText("region: Jakarta")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset Filters" }));
    expect(screen.getByText("No active filters")).toBeInTheDocument();
  });
});
