import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DispatchCenter } from "../pages/DispatchCenter";
import { TestWrapper } from "./TestWrapper";

const mockResponse = (data: unknown) =>
  new Response(JSON.stringify(data), { status: 200, headers: { "Content-Type": "application/json" } });

describe("DispatchCenter", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  it("renders loading state initially", () => {
    vi.mocked(fetch).mockImplementationOnce(() => new Promise(() => undefined));
    render(<TestWrapper><DispatchCenter /></TestWrapper>);
    expect(screen.getByText(/Loading dispatch center/)).toBeDefined();
  });

  it("renders dispatch center with data", async () => {
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        mockResponse({
          total_work_orders: 100, pending: 25, assigned: 30, in_progress: 20, completed: 25, cancelled: 0,
          critical_priority: 5, high_priority: 15,
          orders_by_region: [{ region: "Jakarta", count: 40 }, { region: "Surabaya", count: 30 }],
          orders_by_priority: [{ priority: "High", count: 15 }, { priority: "Critical", count: 5 }],
          orders_by_status: [{ status: "Pending", count: 25 }, { status: "Assigned", count: 30 }],
        })
      )
      .mockResolvedValueOnce(
        mockResponse([
          { work_order_id: "WO-0001", job_type: "Repair", priority: "Critical", region: "Jakarta", service_type: "Mobile", status: "Pending", site_name: "Site Jakarta-01", assigned_technician_id: "", scheduled_start: "2026-08-10" },
          { work_order_id: "WO-0002", job_type: "Maintenance", priority: "High", region: "Surabaya", service_type: "Fiber", status: "Assigned", site_name: "Site Surabaya-02", assigned_technician_id: "TECH-001", scheduled_start: "2026-08-08" },
          { work_order_id: "WO-0003", job_type: "Installation", priority: "Normal", region: "Bandung", service_type: "Broadband", status: "In Progress", site_name: "Site Bandung-03", assigned_technician_id: "TECH-002", scheduled_start: "2026-08-07" },
        ])
      );

    render(<TestWrapper><DispatchCenter /></TestWrapper>);

    expect(await screen.findByText("100")).toBeDefined();
    expect(await screen.findByText("100")).toBeDefined();
    expect(await screen.findByText("Work Order Queue")).toBeDefined();
    expect(await screen.findByText("Assignment Board")).toBeDefined();
  });

  it("handles error state", async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error("Failed to load dispatch data"));
    render(<TestWrapper><DispatchCenter /></TestWrapper>);
    expect(await screen.findByText(/Failed to load dispatch data/)).toBeDefined();
  });
});