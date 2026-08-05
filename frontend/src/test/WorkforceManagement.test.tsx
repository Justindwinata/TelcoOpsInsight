import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { WorkforceManagement } from "../pages/WorkforceManagement";

const mockResponse = (data: unknown) =>
  new Response(JSON.stringify(data), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });

describe("WorkforceManagement", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("renders loading state initially", () => {
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(() => undefined));
    render(<WorkforceManagement />);
    expect(screen.getByText("Loading workforce management")).toBeDefined();
  });

  it("renders workforce dashboard with data", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        mockResponse({
          total_technicians: 50,
          available: 20,
          on_job: 15,
          on_leave: 5,
          off_shift: 10,
          pending_leave_requests: 3,
          approved_leave_requests: 5,
          avg_utilization_rate: 75.5,
          avg_availability_percentage: 85.0,
          technicians_by_region: [
            { region: "Jakarta", count: 20 },
            { region: "Surabaya", count: 15 },
            { region: "Bandung", count: 15 },
          ],
          technicians_by_team: [
            { team: "Field Ops", count: 30 },
            { team: "NOC Core", count: 20 },
          ],
        })
      )
      .mockResolvedValueOnce(
        mockResponse([
          {
            technician_id: "TECH-001",
            name: "Budi",
            assigned_team: "Field Ops",
            region: "Jakarta",
            status: "Available",
            utilization_rate: 0.75,
            first_time_fix_rate: 0.88,
            active_jobs: 3,
            total_jobs_completed: 150,
          },
          {
            technician_id: "TECH-002",
            name: "Siti",
            assigned_team: "NOC Core",
            region: "Surabaya",
            status: "On Job",
            utilization_rate: 0.85,
            first_time_fix_rate: 0.92,
            active_jobs: 5,
            total_jobs_completed: 200,
          },
        ])
      )
      .mockResolvedValueOnce(
        mockResponse([
          {
            leave_id: "LEAVE-001",
            technician_id: "TECH-003",
            leave_type: "Annual",
            start_date: "2026-08-10",
            end_date: "2026-08-14",
            days_requested: 5,
            reason: "Family event",
            status: "Pending",
          },
        ])
      );

    render(<WorkforceManagement />);

    expect(await screen.findByText("50")).toBeDefined();
    expect(await screen.findByText("20")).toBeDefined();
    expect(await screen.findByText("Technician Directory")).toBeDefined();
  });

  it("handles error state", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Network error"));

    render(<WorkforceManagement />);

    expect(await screen.findByText(/Network error/)).toBeDefined();
  });
});