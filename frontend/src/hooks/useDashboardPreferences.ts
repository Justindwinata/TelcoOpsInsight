import { useEffect, useState, type Dispatch, type SetStateAction } from "react";

export interface WidgetConfig {
  id: string;
  title: string;
  enabled: boolean;
  order: number;
}

const DEFAULT_WIDGETS: WidgetConfig[] = [
  { id: "overview", title: "Executive Overview", enabled: true, order: 0 },
  { id: "network-health", title: "Network Health", enabled: true, order: 1 },
  { id: "health-index", title: "Network Health Index", enabled: true, order: 2 },
  { id: "capacity", title: "Capacity Utilization", enabled: true, order: 3 },
  { id: "kpi-comparison", title: "KPI Comparison", enabled: true, order: 4 },
  { id: "incidents", title: "Incident Monitoring", enabled: true, order: 5 },
  { id: "sla", title: "SLA Assurance", enabled: true, order: 6 },
  { id: "tickets", title: "Customer Tickets", enabled: true, order: 7 },
  { id: "technicians", title: "Field Technician Dispatch", enabled: true, order: 8 },
  { id: "regions", title: "Region Performance", enabled: true, order: 9 },
  { id: "recommendations", title: "Recommendations", enabled: true, order: 10 },
  { id: "assets", title: "Asset Management", enabled: true, order: 11 },
  { id: "maintenance", title: "Maintenance Schedule", enabled: true, order: 12 },
  { id: "changes", title: "Change Management", enabled: true, order: 13 },
  { id: "rca", title: "Root Cause Analysis", enabled: true, order: 14 },
  { id: "timeline", title: "Incident Timeline", enabled: true, order: 15 },
  { id: "upload", title: "Data Upload", enabled: true, order: 16 },
  { id: "audit", title: "Audit Logs", enabled: true, order: 17 },
  { id: "report", title: "Report", enabled: true, order: 18 },
];

const STORAGE_KEY = "telcoops-dashboard-prefs";

export function useDashboardPreferences() {
  const [widgets, setWidgets] = useState<WidgetConfig[]>(() => {
    if (typeof window === "undefined") return DEFAULT_WIDGETS;
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Merge with defaults to handle new widgets
        return DEFAULT_WIDGETS.map((def) => {
          const found = parsed.find((p: WidgetConfig) => p.id === def.id);
          return found || def;
        });
      }
    } catch {
      // ignore parse errors
    }
    return DEFAULT_WIDGETS;
  });

  const saveWidgets = (newWidgets: WidgetConfig[]) => {
    setWidgets(newWidgets);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newWidgets));
    } catch {
      // ignore write errors
    }
  };

  const toggleWidget = (id: string) => {
    saveWidgets(
      widgets.map((w) => (w.id === id ? { ...w, enabled: !w.enabled } : w))
    );
  };

  const reorderWidgets = (fromIndex: number, toIndex: number) => {
    const newWidgets = [...widgets];
    const [removed] = newWidgets.splice(fromIndex, 1);
    newWidgets.splice(toIndex, 0, removed);
    saveWidgets(newWidgets.map((w, i) => ({ ...w, order: i })));
  };

  const moveWidget = (id: string, direction: "up" | "down") => {
    const index = widgets.findIndex((w) => w.id === id);
    if (index === -1) return;
    const newIndex = direction === "up" ? index - 1 : index + 1;
    if (newIndex < 0 || newIndex >= widgets.length) return;
    reorderWidgets(index, newIndex);
  };

  const resetToDefaults = () => {
    saveWidgets(DEFAULT_WIDGETS);
  };

  const enabledWidgets = widgets.filter((w) => w.enabled).sort((a, b) => a.order - b.order);

  return {
    widgets,
    enabledWidgets,
    toggleWidget,
    moveWidget,
    resetToDefaults,
  };
}

export function usePersistedState<T>(key: string, initialValue: T): [T, Dispatch<SetStateAction<T>>] {
  const [state, setState] = useState<T>(() => {
    if (typeof window === "undefined") return initialValue;
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initialValue;
    } catch {
      return initialValue;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {
      // ignore
    }
  }, [key, state]);

  return [state, setState];
}