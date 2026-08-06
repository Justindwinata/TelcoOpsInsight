import { describe, it, expect } from "vitest";
import { render } from "@testing-library/react";
import { ErrorBoundary } from "../components/ErrorBoundary";

describe("ErrorBoundary", () => {
  it("renders children when no error", () => {
    const { container } = render(
      <ErrorBoundary>
        <div>Test child</div>
      </ErrorBoundary>
    );
    expect(container.textContent).toContain("Test child");
  });
});
