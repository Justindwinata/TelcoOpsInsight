import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NotificationProvider } from "../components/NotificationManager";

describe("NotificationManager", () => {
  it("renders provider without crashing", () => {
    const { container } = render(
      <NotificationProvider>
        <div>Test</div>
      </NotificationProvider>
    );
    expect(container.textContent).toContain("Test");
  });
});
