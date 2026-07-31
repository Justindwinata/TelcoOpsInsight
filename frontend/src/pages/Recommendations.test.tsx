import { render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { storeAuth, clearAuth } from "../api/client";
import { FilterProvider } from "../filters/FilterContext";
import { Recommendations } from "./Recommendations";

describe("Recommendations", () => {
  afterEach(() => {
    clearAuth();
    vi.restoreAllMocks();
  });

  it("renders recommendation severity and supporting action", async () => {
    storeAuth({
      access_token: "token",
      token_type: "bearer",
      user: { username: "noc_manager", display_name: "NOC Manager Demo", role: "NOC Manager", permissions: ["dashboard:read"] }
    });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            recommendations: [
              {
                rule_id: "RULE-001",
                severity: "High",
                metric: "sla_achievement",
                condition: "<",
                threshold: 98,
                observed_value: 97.5,
                supporting_metric_value: 97.5,
                trigger_condition: "sla_achievement < 98",
                affected_region: "Jakarta",
                affected_service: "Fiber Internet",
                recommendation_title: "Recover SLA performance",
                recommendation_text: "Review breached services.",
                explanation: "Observed SLA triggered this rule.",
                recommended_action: "Open a recovery plan.",
                recommended_owner: "Customer Assurance",
                region: "Jakarta"
              }
            ],
            triggered_count: 1,
            rules_evaluated: 44,
            method: "deterministic_rule_based"
          })
      })
    );

    render(
      <FilterProvider>
        <Recommendations />
      </FilterProvider>
    );

    expect(await screen.findByText("High")).toBeInTheDocument();
    expect(screen.getByText("Open a recovery plan.")).toBeInTheDocument();
  });
});
