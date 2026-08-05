import { useEffect, useMemo, useState } from "react";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { FilterPanel } from "./components/FilterPanel";
import { FilterProvider } from "./filters/FilterContext";
import { AssetManagement } from "./pages/AssetManagement";
import { AuditLogs } from "./pages/AuditLogs";
import { ChangeManagement } from "./pages/ChangeManagement";
import { DataUpload } from "./pages/DataUpload";
import { DispatchCenter } from "./pages/DispatchCenter";
import { ExecutiveOverview } from "./pages/ExecutiveOverview";
import { FieldTechnicians } from "./pages/FieldTechnicians";
import { Incidents } from "./pages/Incidents";
import { MaintenanceSchedule } from "./pages/MaintenanceSchedule";
import { NetworkHealth } from "./pages/NetworkHealth";
import { Recommendations } from "./pages/Recommendations";
import { RegionPerformance } from "./pages/RegionPerformance";
import { Report } from "./pages/Report";
import { RootCauseAnalysis } from "./pages/RootCauseAnalysis";
import { IncidentTimeline } from "./pages/IncidentTimeline";
import { SlaAssurance } from "./pages/SlaAssurance";
import { Tickets } from "./pages/Tickets";
import { Login } from "./pages/Login";
import { NetworkHealthIndex, CapacityUtilization, KpiComparison } from "./pages/AdvancedAnalytics";
import { ExecutiveIntelligence } from "./pages/ExecutiveIntelligence";
import { NetworkMap } from "./pages/NetworkMap";

const sections = [
  "Executive Overview",
  "Executive Intelligence",
  "Network Health",
  "Network Map",
  "Network Health Index",
  "Capacity Utilization",
  "KPI Comparison",
  "Incident Monitoring",
  "SLA Assurance",
  "Customer Tickets",
  "Field Technician Dispatch",
  "Dispatch Center",
  "Workforce Management",
  "Service Requests",
  "Region Performance",
  "Recommendations",
  "Asset Management",
  "Maintenance Schedule",
  "Change Management",
  "Root Cause Analysis",
  "Incident Timeline",
  "SLA Monitoring",
  "Capacity Planning",
  "Executive Decision Center",
  "Data Upload",
  "Audit Logs",
  "Report"
] as const;

export type Section = (typeof sections)[number];

function renderSection(section: Section) {
  switch (section) {
    case "Executive Overview":
      return <ExecutiveOverview />;
    case "Executive Intelligence":
      return <ExecutiveIntelligence />;
    case "Network Health":
      return <NetworkHealth />;
    case "Network Map":
      return <NetworkMap />;
    case "Network Health Index":
      return <NetworkHealthIndex />;
    case "Capacity Utilization":
      return <CapacityUtilization />;
    case "KPI Comparison":
      return <KpiComparison />;
    case "Incident Monitoring":
      return <Incidents />;
    case "SLA Assurance":
      return <SlaAssurance />;
    case "Customer Tickets":
      return <Tickets />;
    case "Field Technician Dispatch":
      return <FieldTechnicians />;
    case "Dispatch Center":
      return <DispatchCenter />;
    case "Workforce Management":
      return <WorkforceManagement />;
    case "Service Requests":
      return <EmptyState />;
    case "Region Performance":
      return <RegionPerformance />;
    case "Recommendations":
      return <Recommendations />;
    case "Asset Management":
      return <AssetManagement />;
    case "Maintenance Schedule":
      return <MaintenanceSchedule />;
    case "Change Management":
      return <ChangeManagement />;
    case "Root Cause Analysis":
      return <RootCauseAnalysis />;
    case "Incident Timeline":
      return <IncidentTimeline />;
    case "SLA Monitoring":
      return <EmptyState />;
    case "Capacity Planning":
      return <EmptyState />;
    case "Executive Decision Center":
      return <EmptyState />;
    case "Data Upload":
      return <DataUpload />;
    case "Audit Logs":
      return <AuditLogs />;
    case "Report":
      return <Report />;
  }
}

function AppContent() {
  const [activeSection, setActiveSection] = useState<Section>("Executive Overview");
  const { user, logout, hasPermission } = useAuth();

  const visibleSections = useMemo(
    () =>
      sections.filter((section) => {
        if (section === "Data Upload") {
          return (
            hasPermission("datasets:validate") ||
            hasPermission("datasets:import") ||
            hasPermission("datasets:seed") ||
            hasPermission("imports:read")
          );
        }
        if (section === "Report") {
          return hasPermission("reports:read");
        }
        if (section === "Audit Logs") {
          return hasPermission("audit:read");
        }
        if (section === "Recommendations") {
          return hasPermission("recommendations:read");
        }
        return hasPermission("dashboard:read");
      }),
    [hasPermission]
  );

  useEffect(() => {
    if (!visibleSections.includes(activeSection)) {
      setActiveSection("Executive Overview");
    }
  }, [activeSection, visibleSections]);

  if (!user) {
    return <Login />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <span className="eyebrow">NusaTel Digital Network</span>
          <h1>TelcoOps Insight</h1>
          <p>Network Operations and Service Assurance Dashboard</p>
        </div>
        <nav className="nav-list" aria-label="Dashboard sections">
          {visibleSections.map((section) => (
            <button
              key={section}
              type="button"
              className={section === activeSection ? "active" : ""}
              onClick={() => setActiveSection(section)}
            >
              {section}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Network Operations Center</span>
            <h2>{activeSection}</h2>
          </div>
          <span className="data-pill">Synthetic 2026 Dataset</span>
          <div className="user-chip">
            <span>{user.display_name}</span>
            <strong>{user.role}</strong>
            <button type="button" onClick={() => void logout()}>
              Logout
            </button>
          </div>
        </header>
        <FilterPanel />
        {renderSection(activeSection)}
      </main>
    </div>
  );
}

export function App() {
  return (
    <AuthProvider>
      <FilterProvider>
        <AppContent />
      </FilterProvider>
    </AuthProvider>
  );
}
