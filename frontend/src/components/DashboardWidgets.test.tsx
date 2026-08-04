import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExecutiveIntelligence } from "../pages/ExecutiveIntelligence";

describe("ExecutiveIntelligence", () => {
  it("renders loading state", () => {
    render(<ExecutiveIntelligence />);
    expect(screen.getByText(/Loading/i)).toBeDefined();
  });
});

describe("DashboardWidgets", () => {
  it("MetricList renders items", () => {
    const { MetricList } = require("../components/DashboardWidgets");
    const items = [
      { label: "Uptime", value: "99.5%" },
      { label: "Incidents", value: 5 },
    ];
    render(<MetricList items={items} />);
    expect(screen.getByText("Uptime")).toBeDefined();
    expect(screen.getByText("99.5%")).toBeDefined();
  });

  it("Panel renders with badge", () => {
    const { Panel } = require("../components/DashboardWidgets");
    render(
      <Panel title="Test Panel" badge={3}>
        <p>Content</p>
      </Panel>
    );
    expect(screen.getByText("Test Panel")).toBeDefined();
    expect(screen.getByText("3")).toBeDefined();
  });

  it("KpiGrid renders multiple items", () => {
    const { KpiGrid } = require("../components/DashboardWidgets");
    const items = [
      { label: "KPI 1", value: 100, tone: "healthy" },
      { label: "KPI 2", value: 50, tone: "warning" },
    ];
    render(<KpiGrid items={items} />);
    expect(screen.getByText("KPI 1")).toBeDefined();
    expect(screen.getByText("KPI 2")).toBeDefined();
  });

  it("DataTable renders rows", () => {
    const { DataTable } = require("../components/DashboardWidgets");
    const columns = [
      { key: "name", label: "Name" },
      { key: "value", label: "Value" },
    ];
    const data = [
      { name: "Item 1", value: 10 },
      { name: "Item 2", value: 20 },
    ];
    render(<DataTable columns={columns} data={data} />);
    expect(screen.getByText("Name")).toBeDefined();
    expect(screen.getByText("Item 1")).toBeDefined();
  });
});
