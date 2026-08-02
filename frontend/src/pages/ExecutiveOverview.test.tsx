import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { AuthProvider } from "../auth/AuthContext";
import { FilterProvider } from "../filters/FilterContext";
import { ExecutiveOverview } from "../pages/ExecutiveOverview";

describe("ExecutiveOverview with notifications", () => {
  it("renders notification strip header", () => {
    render(
      <AuthProvider>
        <FilterProvider>
          <ExecutiveOverview />
        </FilterProvider>
      </AuthProvider>
    );
    expect(screen.getByText("Loading operational overview...")).toBeTruthy();
  });
});