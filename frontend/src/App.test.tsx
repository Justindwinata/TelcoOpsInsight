import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { clearAuth, storeAuth } from "./api/client";

function storeDemoUser(role = "NOC Manager", permissions = ["dashboard:read", "datasets:seed", "datasets:validate", "datasets:import"]) {
  storeAuth({
    access_token: "test-token",
    token_type: "bearer",
    user: {
      username: "noc_manager",
      display_name: "NOC Manager Demo",
      role,
      permissions
    }
  });
}

describe("App", () => {
  afterEach(() => {
    clearAuth();
  });

  it("renders the login page before authentication", () => {
    render(<App />);

    expect(screen.getByText("Local authentication prototype for the service assurance dashboard.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign In" })).toBeInTheDocument();
  });

  it("renders the NOC dashboard shell", () => {
    storeDemoUser();
    render(<App />);

    expect(screen.getByText("TelcoOps Insight")).toBeInTheDocument();
    expect(screen.getAllByText("Executive Overview").length).toBeGreaterThan(0);
    expect(screen.getByText("Synthetic 2026 Dataset")).toBeInTheDocument();
    expect(screen.getByText("NOC Manager Demo")).toBeInTheDocument();
  });

  it("switches dashboard sections from the sidebar", () => {
    storeDemoUser();
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Recommendations" }));

    expect(screen.getAllByText("Recommendations").length).toBeGreaterThan(0);
    expect(screen.getByText("Loading recommendations...")).toBeInTheDocument();
  });
});
