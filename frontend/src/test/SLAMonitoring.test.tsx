import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { SLAMonitoring } from "../pages/SLAMonitoring";
import { TestWrapper } from "./TestWrapper";

const mockResponse = (data: unknown) =>
  new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } });

describe("SLAMonitoring", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("renders loading state initially", () => {
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(() => undefined));
    render(<TestWrapper><SLAMonitoring /></TestWrapper>);
    expect(screen.getByText(/Loading SLA monitoring/)).toBeDefined();
  });

  it("renders SLA dashboard with data", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        mockResponse({
          total_sla_records: 200, breached_records: 15, at_risk_records: 30, compliant_records: 155,
          breach_rate: 7.5, avg_mttr_minutes: 45.2, avg_response_time_minutes: 12.5, avg_resolution_time_minutes: 65.3,
          by_severity: { Critical: 5, High: 10, Medium: 15, Low: 20 },
          by_region: [{ region: "Jakarta", breached: 5, at_risk: 10, compliant: 50 }, { region: "Surabaya", breached: 3, at_risk: 8, compliant: 45 }],
          by_service: [{ service: "Mobile", breached: 7, at_risk: 12, compliant: 60 }, { service: "Fiber", breached: 5, at_risk: 10, compliant: 55 }],
        })
      )
      .mockResolvedValueOnce(
        mockResponse({
          heatmap: {
            Jakarta: { Mobile: { sla_target: 99.0, sla_actual: 98.5, compliance: 99.5, breached_count: 2, total_count: 50 }, Fiber: { sla_target: 99.0, sla_actual: 99.2, compliance: 100.2, breached_count: 0, total_count: 45 } },
            Surabaya: { Mobile: { sla_target: 99.0, sla_actual: 97.8, compliance: 98.8, breached_count: 3, total_count: 40 }, Fiber: { sla_target: 99.0, sla_actual: 98.9, compliance: 99.9, breached_count: 1, total_count: 38 } },
          },
          regions: ["Jakarta", "Surabaya"],
        })
      );

    render(<TestWrapper><SLAMonitoring /></TestWrapper>);
    expect(await screen.findByText("200")).toBeDefined();
    expect(await screen.findByText("15")).toBeDefined();
    expect(await screen.findByText("SLA Heatmap")).toBeDefined();
    expect(await screen.findByText("Breach Severity Distribution")).toBeDefined();
  });

  it("handles error state", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Failed to load SLA data"));
    render(<TestWrapper><SLAMonitoring /></TestWrapper>);
    expect(await screen.findByText(/Failed to load SLA data/)).toBeDefined();
  });
});