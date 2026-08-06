import { useState, useEffect } from "react";

type DashboardPreferences = {
  darkMode: boolean;
  sidebarCollapsed: boolean;
  autoRefreshInterval: number;
  chartTheme: "light" | "dark";
  lastViewedSection: string;
};

export function useDashboardPreferences() {
  const [prefs, setPrefs] = useState<DashboardPreferences>({
    darkMode: localStorage.getItem("telcoops_darkMode") === "true",
    sidebarCollapsed: localStorage.getItem("telcoops_sidebarCollapsed") === "true",
    autoRefreshInterval: parseInt(localStorage.getItem("telcoops_autoRefresh") || "30"),
    chartTheme: localStorage.getItem("telcoops_chartTheme") as "light" | "dark" || "light",
    lastViewedSection: localStorage.getItem("telcoops_lastSection") || "Executive Overview",
  });

  const updatePref = (key: keyof DashboardPreferences, value: any) => {
    setPrefs((prev) => {
      const updated = { ...prev, [key]: value };
      localStorage.setItem(`telcoops_${key}`, String(value));
      return updated;
    });
  };

  const toggleDarkMode = () => updatePref("darkMode", !prefs.darkMode);
  const toggleSidebar = () => updatePref("sidebarCollapsed", !prefs.sidebarCollapsed);
  const setRefreshInterval = (interval: number) => updatePref("autoRefreshInterval", interval);

  return { prefs, updatePref, toggleDarkMode, toggleSidebar, setRefreshInterval };
}
