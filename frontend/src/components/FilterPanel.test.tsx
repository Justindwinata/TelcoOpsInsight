import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { FilterPanel } from "./FilterPanel";
import { FilterProvider, useDashboardFilters } from "../filters/FilterContext";

function QueryProbe() {
  const { queryString } = useDashboardFilters();
  return <output aria-label="query">{queryString}</output>;
}

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

    expect(screen.getByText("Region: Jakarta")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Reset Filters" }));
    expect(screen.getByText("No active filters")).toBeInTheDocument();
  });

  it("shows invalid range message and suppresses query params", () => {
    render(
      <FilterProvider>
        <FilterPanel />
        <QueryProbe />
      </FilterProvider>
    );

    fireEvent.change(screen.getByLabelText("Start Date"), { target: { value: "2026-02-10" } });
    fireEvent.change(screen.getByLabelText("End Date"), { target: { value: "2026-02-01" } });

    expect(screen.getByText("Start date must be before or equal to end date.")).toBeInTheDocument();
    expect(screen.getByLabelText("query")).toHaveTextContent("");
  });
});
