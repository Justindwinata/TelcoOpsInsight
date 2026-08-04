import { createContext, useContext, useMemo, useState } from "react";

export type DashboardFilters = {
  start_date: string;
  end_date: string;
  month: string;
  region: string;
  service_type: string;
  severity: string;
  status: string;
  team: string;
};

const STORAGE_KEY = "telcoops_dashboard_filters";
const emptyFilters: DashboardFilters = {
  start_date: "",
  end_date: "",
  month: "",
  region: "",
  service_type: "",
  severity: "",
  status: "",
  team: ""
};

type FilterContextValue = {
  filters: DashboardFilters;
  setFilter: (key: keyof DashboardFilters, value: string) => void;
  resetFilters: () => void;
  queryString: string;
  activeSummary: string;
  hasActiveFilters: boolean;
  validationMessage: string | null;
};

const FilterContext = createContext<FilterContextValue | null>(null);

function loadFilters(): DashboardFilters {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return emptyFilters;
  }
  try {
    return { ...emptyFilters, ...(JSON.parse(raw) as Partial<DashboardFilters>) };
  } catch {
    return emptyFilters;
  }
}

export function FilterProvider({ children }: { children: React.ReactNode }) {
  const [filters, setFilters] = useState<DashboardFilters>(() => loadFilters());

  const value = useMemo<FilterContextValue>(() => {
    const validationMessage =
      filters.start_date && filters.end_date && filters.start_date > filters.end_date
        ? "Start date must be before or equal to end date."
        : null;
    const params = new URLSearchParams();
    if (!validationMessage) {
      Object.entries(filters).forEach(([key, filterValue]) => {
        if (filterValue) {
          params.set(key, filterValue);
        }
      });
    }
    const labels: Record<string, string> = {
      start_date: "Start date",
      end_date: "End date",
      month: "Month",
      region: "Region",
      service_type: "Service",
      severity: "Severity",
      status: "Status",
      team: "Team"
    };
    const active = Object.entries(filters)
      .filter(([, filterValue]) => Boolean(filterValue))
      .map(([key, filterValue]) => `${labels[key] ?? key}: ${filterValue}`);
    const hasActiveFilters = active.length > 0;
    return {
      filters,
      setFilter(key, filterValue) {
        setFilters((current) => {
          const next = { ...current, [key]: filterValue };
          if (key === "month" && filterValue) {
            next.start_date = "";
            next.end_date = "";
          }
          if ((key === "start_date" || key === "end_date") && filterValue) {
            next.month = "";
          }
          localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
          return next;
        });
      },
      resetFilters() {
        localStorage.removeItem(STORAGE_KEY);
        setFilters(emptyFilters);
      },
      queryString: params.toString() ? `?${params.toString()}` : "",
      activeSummary: hasActiveFilters ? active.join(" / ") : "No active filters",
      hasActiveFilters,
      validationMessage
    };
  }, [filters]);

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useDashboardFilters() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useDashboardFilters must be used inside FilterProvider");
  }
  return context;
}
