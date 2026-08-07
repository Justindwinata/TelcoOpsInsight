import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { AlarmManagement } from "../pages/AlarmManagement";
import { TestWrapper } from "./TestWrapper";

const mockResponse = (data: unknown) =>
  new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } });

describe("AlarmManagement", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("renders loading state initially", () => {
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(() => undefined));
    render(<TestWrapper><AlarmManagement /></TestWrapper>);
    expect(screen.getByText(/Loading alarms/)).toBeDefined();
  });

  it("renders alarm dashboard with data", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(mockResponse({ total_active: 15, by_severity: { Critical: 2, Major: 5, Minor: 8 }, by_status: { Active: 10, Acknowledged: 5 } }))
      .mockResolvedValueOnce(mockResponse([
        { alarm_id: "ALM-001", severity: "Critical", category: "Network", site_id: "SITE-001", service_type: "Mobile", occurrence_count: 3, status: "Active" },
      ]));

    render(<TestWrapper><AlarmManagement /></TestWrapper>);
    expect(await screen.findByText("15")).toBeDefined();
    expect(await screen.findByText("Alarm Queue")).toBeDefined();
  });

  it("handles error state", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Failed to load"));
    render(<TestWrapper><AlarmManagement /></TestWrapper>);
    expect(await screen.findByText(/Failed to load/)).toBeDefined();
  });
});