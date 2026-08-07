import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { RefreshIndicator } from "../components/RefreshIndicator";

describe("RefreshIndicator", () => {
  it("renders connected status", () => {
    render(
      <RefreshIndicator
        status="connected"
        lastUpdate={new Date("2026-08-06T12:00:00")}
        eventRate={5}
        totalEvents={100}
      />
    );
    expect(screen.getByText(/Connected/)).toBeDefined();
    expect(screen.getByText(/100/)).toBeDefined();
  });

  it("renders paused status", () => {
    render(
      <RefreshIndicator
        status="paused"
        lastUpdate={null}
        eventRate={0}
        totalEvents={0}
      />
    );
    expect(screen.getByText(/Paused/)).toBeDefined();
  });

  it("renders disconnected status", () => {
    render(
      <RefreshIndicator
        status="disconnected"
        lastUpdate={null}
        eventRate={0}
        totalEvents={0}
      />
    );
    expect(screen.getByText(/Disconnected/)).toBeDefined();
  });
});