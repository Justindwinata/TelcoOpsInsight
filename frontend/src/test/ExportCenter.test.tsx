import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { ExportCenter } from "../pages/ExportCenter";

describe("ExportCenter", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
    vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:test"), revokeObjectURL: vi.fn() });
  });

  it("renders export center with options", () => {
    render(<ExportCenter />);
    expect(screen.getByText("Export Center")).toBeDefined();
    expect(screen.getByText(/Incident History/)).toBeDefined();
    expect(screen.getByText(/Alarm History/)).toBeDefined();
  });

  it("allows selecting export type", () => {
    render(<ExportCenter />);
    const alarmRadio = screen.getByLabelText(/Alarm History/);
    fireEvent.click(alarmRadio);
    expect(alarmRadio).toBeChecked();
  });

  it("triggers CSV export", async () => {
    const mockBlob = new Blob(["test"], { type: "text/csv" });
    vi.mocked(fetch).mockResolvedValueOnce({ ok: true, blob: async () => mockBlob } as Response);
    
    render(<ExportCenter />);
    const csvButton = screen.getByText("Export CSV");
    fireEvent.click(csvButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/exports/incidents/csv", expect.any(Object));
    });
  });

  it("triggers JSON export", async () => {
    const mockBlob = new Blob(["{}"], { type: "application/json" });
    vi.mocked(fetch).mockResolvedValueOnce({ ok: true, blob: async () => mockBlob } as Response);
    
    render(<ExportCenter />);
    const jsonButton = screen.getByText("Export JSON");
    fireEvent.click(jsonButton);
    
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/exports/incidents/json", expect.any(Object));
    });
  });
});
