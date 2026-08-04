import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExecutiveIntelligence } from "../pages/ExecutiveIntelligence";

describe("ExecutiveIntelligence", () => {
  it("renders loading state", () => {
    render(<ExecutiveIntelligence />);
    expect(screen.getByText(/Loading/i)).toBeDefined();
  });
});
