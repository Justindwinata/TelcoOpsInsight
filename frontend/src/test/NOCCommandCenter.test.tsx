import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { NOCCommandCenter } from "../pages/NOCCommandCenter";
import { TestWrapper } from "./TestWrapper";

const mockResponse = (data: unknown) =>
  new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } });

describe("NOCCommandCenter", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("renders loading state initially", () => {
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(() => undefined));
    render(<TestWrapper><NOCCommandCenter /></TestWrapper>);
    expect(screen.getByText(/Loading NOC command center/)).toBeDefined();
  });

  it("renders NOC dashboard with data", async () => {
    vi.mocked(fetch).mockResolvedValueOnce(
      mockResponse({
        network_overview: { network_uptime_pct: 99.5, total_sites: 150, online_sites: 148, avg_latency_ms: 25.3, avg_packet_loss_pct: 0.02, active_incidents: 3, critical_incidents: 1 },
        regional_health: [{ region: "Jakarta", sites: 50, avg_latency_ms: 22, avg_packet_loss_pct: 0.01, active_incidents: 1, health_score: 95.0 }],
        critical_incidents: [],
        active_alarms: [],
        sla_status: { total_records: 200, breached: 5, at_risk: 10, breach_rate_pct: 2.5, avg_mttr_minutes: 35 },
        technician_availability: { total: 50, available: 20, on_job: 25, on_leave: 5, utilization_pct: 75.0 },
        dispatch_status: { pending: 5, assigned: 10, in_progress: 8, completed: 15, critical_priority: 2 },
        maintenance_today: [],
        executive_kpis: { network_health: "Excellent", incident_velocity: 3, sla_compliance_pct: 97.5 },
      })
    );
    render(<TestWrapper><NOCCommandCenter /></TestWrapper>);
    expect(await screen.findByText("99.5%")).toBeDefined();
    expect(await screen.findByText("Regional Health")).toBeDefined();
  });

  it("handles error state", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));
    render(<TestWrapper><NOCCommandCenter /></TestWrapper>);
    expect(await screen.findByText(/Network error/)).toBeDefined();
  });
});
