import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExecutiveIntelligence } from "../pages/ExecutiveIntelligence";
import { TestWrapper } from "../test/TestWrapper";

describe("ExecutiveIntelligence", () => {
  it("renders loading state", () => {
    render(<TestWrapper><ExecutiveIntelligence /></TestWrapper>);
    expect(screen.getByText(/Loading/i)).toBeDefined();
  });
});