import { useState } from "react";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { DataUpload } from "./pages/DataUpload";
import { ExecutiveOverview } from "./pages/ExecutiveOverview";
import { FieldTechnicians } from "./pages/FieldTechnicians";
import { Incidents } from "./pages/Incidents";
import { NetworkHealth } from "./pages/NetworkHealth";
import { Recommendations } from "./pages/Recommendations";
import { RegionPerformance } from "./pages/RegionPerformance";
import { Report } from "./pages/Report";
import { SlaAssurance } from "./pages/SlaAssurance";
import { Tickets } from "./pages/Tickets";
import { Login } from "./pages/Login";

const sections = [
  "Executive Overview",
  "Network Health",
  "Incident Monitoring",
  "SLA Assurance",
  "Customer Tickets",
  "Field Technician Dispatch",
  "Region Performance",
  "Recommendations",
  "Data Upload",
  "Report"
] as const;

export type Section = (typeof sections)[number];

function renderSection(section: Section) {
  switch (section) {
    case "Executive Overview":
      return <ExecutiveOverview />;
    case "Network Health":
      return <NetworkHealth />;
    case "Incident Monitoring":
      return <Incidents />;
    case "SLA Assurance":
      return <SlaAssurance />;
    case "Customer Tickets":
      return <Tickets />;
    case "Field Technician Dispatch":
      return <FieldTechnicians />;
    case "Region Performance":
      return <RegionPerformance />;
    case "Recommendations":
      return <Recommendations />;
    case "Data Upload":
      return <DataUpload />;
    case "Report":
      return <Report />;
  }
}

function AppContent() {
  const [activeSection, setActiveSection] = useState<Section>("Executive Overview");
  const { user, logout } = useAuth();

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
          {sections.map((section) => (
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
        {renderSection(activeSection)}
      </main>
    </div>
  );
}

export function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
