import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";
import { App } from "./App";
import { clearAuth, storeAuth } from "./api/client";

function storeDemoUser(
  role = "NOC Manager",
  permissions = [
    "dashboard:read",
    "datasets:seed",
    "datasets:validate",
    "datasets:import",
    "imports:read",
    "reports:read",
    "recommendations:read",
    "audit:read"
  ]
) {
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

  it("renders the NOC dashboard shell", async () => {
    storeDemoUser();
    render(<App />);

    await waitFor(() => expect(screen.getByText("TelcoOps Insight")).toBeInTheDocument());
    expect(screen.getAllByText("Executive Overview").length).toBeGreaterThan(0);
    expect(screen.getByText("Synthetic 2026 Dataset")).toBeInTheDocument();
    expect(screen.getByText("NOC Manager Demo")).toBeInTheDocument();
  });

  it("switches dashboard sections from the sidebar", async () => {
    storeDemoUser();
    render(<App />);

    await waitFor(() => expect(screen.getByRole("button", { name: "Recommendations" })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: "Recommendations" }));

    expect(screen.getAllByText("Recommendations").length).toBeGreaterThan(0);
    expect(screen.getByText("Loading recommendations...")).toBeInTheDocument();
  });

  it("shows audit navigation only to audit readers", async () => {
    storeDemoUser();
    const { rerender } = render(<App />);
    await waitFor(() => expect(screen.getByRole("button", { name: "Audit Logs" })).toBeInTheDocument());

    clearAuth();
    storeDemoUser("Viewer", ["dashboard:read", "reports:read"]);
    rerender(<App />);

    await waitFor(() => expect(screen.queryByRole("button", { name: "Audit Logs" })).not.toBeInTheDocument());
  });
});
