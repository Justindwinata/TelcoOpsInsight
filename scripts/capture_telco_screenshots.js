#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const OUT_DIR = path.join(ROOT, "docs", "evidence", "screenshots", "final");
const FRONTEND_URL = process.env.TELCOOPS_FRONTEND_URL ?? "http://127.0.0.1:5173";
const DEMO_USERNAME = process.env.TELCOOPS_DEMO_USER ?? "noc_manager";
const DEMO_PASSWORD = process.env.TELCOOPS_DEMO_PASSWORD ?? "telco-demo-2026";

const shots = [
  ["login", null],
  ["executive-overview", "Executive Overview"],
  ["network-health", "Network Health"],
  ["incident-monitoring", "Incident Monitoring"],
  ["sla-assurance", "SLA Assurance"],
  ["customer-tickets", "Customer Tickets"],
  ["technician-dispatch", "Field Technician Dispatch"],
  ["recommendations", "Recommendations"],
  ["import-history", "Data Upload"],
  ["audit-logs", "Audit Logs"],
  ["report", "Report"]
];

async function loadPlaywright() {
  try {
    return await import("playwright");
  } catch (error) {
    throw new Error(
      "Playwright is not installed. Run this workflow after installing Playwright in frontend devDependencies, " +
        "then start backend and frontend before capture."
    );
  }
}

async function capture() {
  const { chromium } = await loadPlaywright();
  await fs.mkdir(OUT_DIR, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });
  try {
    await page.goto(FRONTEND_URL, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(OUT_DIR, "01-login.png"), fullPage: true });
    await page.getByLabel("Username").fill(DEMO_USERNAME);
    await page.getByLabel("Password").fill(DEMO_PASSWORD);
    await page.getByRole("button", { name: "Sign In" }).click();
    await page.getByText("TelcoOps Insight").waitFor();

    let index = 2;
    for (const [name, section] of shots.slice(1)) {
      if (section) {
        await page.getByRole("button", { name: section }).click();
      }
      await page.waitForTimeout(750);
      await page.screenshot({ path: path.join(OUT_DIR, `${String(index).padStart(2, "0")}-${name}.png`), fullPage: true });
      index += 1;
    }

    await page.setViewportSize({ width: 390, height: 844 });
    await page.getByRole("button", { name: "Executive Overview" }).click();
    await page.waitForTimeout(750);
    await page.screenshot({ path: path.join(OUT_DIR, "12-mobile-overview.png"), fullPage: true });
  } finally {
    await browser.close();
  }
  console.log(JSON.stringify({ captured: true, output_dir: OUT_DIR }, null, 2));
}

capture().catch((error) => {
  console.error(JSON.stringify({ captured: false, reason: error.message, output_dir: OUT_DIR }, null, 2));
  process.exit(1);
});
