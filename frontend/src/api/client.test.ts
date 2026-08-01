import { afterEach, describe, expect, it, vi } from "vitest";
import { apiGet, clearAuth, getStoredToken, storeAuth, uploadCsv } from "./client";

describe("api client", () => {
  afterEach(() => {
    clearAuth();
    vi.restoreAllMocks();
  });

  it("attaches bearer token to API requests", async () => {
    storeAuth({
      access_token: "abc123",
      token_type: "bearer",
      user: { username: "viewer", display_name: "Viewer Demo", role: "Viewer", permissions: ["dashboard:read"] }
    });
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ ok: true }) });
    vi.stubGlobal("fetch", fetchMock);

    await apiGet("/api/dashboard/overview?region=Jakarta");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/dashboard/overview?region=Jakarta",
      expect.objectContaining({ headers: { Authorization: "Bearer abc123" } })
    );
  });

  it("sends persisted upload query parameter", async () => {
    storeAuth({
      access_token: "abc123",
      token_type: "bearer",
      user: { username: "noc_manager", display_name: "NOC Manager Demo", role: "NOC Manager", permissions: ["datasets:import"] }
    });
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: () => Promise.resolve({ accepted: true }) });
    vi.stubGlobal("fetch", fetchMock);
    const file = new File(["site_id\nSITE-0001\n"], "network_sites.csv", { type: "text/csv" });

    await uploadCsv(file, true);

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/datasets/upload?persist=true",
      expect.objectContaining({ method: "POST", headers: { Authorization: "Bearer abc123" } })
    );
  });

  it("clears stored auth when API returns 401", async () => {
    storeAuth({
      access_token: "expired",
      token_type: "bearer",
      user: { username: "viewer", display_name: "Viewer Demo", role: "Viewer", permissions: ["dashboard:read"] }
    });
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: false, status: 401, json: () => Promise.resolve({ detail: "Session expired" }) })
    );

    await expect(apiGet("/api/auth/me")).rejects.toThrow("Session expired");

    expect(getStoredToken()).toBeNull();
  });
});
