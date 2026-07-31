import { useDashboardFilters } from "../filters/FilterContext";

const regions = ["Jakarta", "Bandung", "Surabaya", "Medan", "Makassar", "Semarang", "Yogyakarta", "Denpasar", "Palembang", "Balikpapan"];
const services = ["Fiber Internet", "Mobile Broadband", "Enterprise VPN", "IPTV", "Voice", "Cloud Connectivity"];
const severities = ["Low", "Medium", "High", "Critical"];
const statuses = ["Open", "Investigating", "Escalated", "Resolved", "Closed", "In Progress", "Waiting Customer"];
const months = Array.from({ length: 12 }, (_, index) => `2026-${String(index + 1).padStart(2, "0")}`);

export function FilterPanel() {
  const { filters, setFilter, resetFilters, activeSummary } = useDashboardFilters();

  return (
    <section className="filter-panel">
      <div className="filter-grid">
        <label>
          Start Date
          <input type="date" value={filters.start_date} onChange={(event) => setFilter("start_date", event.target.value)} />
        </label>
        <label>
          End Date
          <input type="date" value={filters.end_date} onChange={(event) => setFilter("end_date", event.target.value)} />
        </label>
        <label>
          Month
          <select value={filters.month} onChange={(event) => setFilter("month", event.target.value)}>
            <option value="">All months</option>
            {months.map((month) => (
              <option key={month} value={month}>
                {month}
              </option>
            ))}
          </select>
        </label>
        <label>
          Region
          <select value={filters.region} onChange={(event) => setFilter("region", event.target.value)}>
            <option value="">All regions</option>
            {regions.map((region) => (
              <option key={region} value={region}>
                {region}
              </option>
            ))}
          </select>
        </label>
        <label>
          Service
          <select value={filters.service_type} onChange={(event) => setFilter("service_type", event.target.value)}>
            <option value="">All services</option>
            {services.map((service) => (
              <option key={service} value={service}>
                {service}
              </option>
            ))}
          </select>
        </label>
        <label>
          Severity
          <select value={filters.severity} onChange={(event) => setFilter("severity", event.target.value)}>
            <option value="">All severities</option>
            {severities.map((severity) => (
              <option key={severity} value={severity}>
                {severity}
              </option>
            ))}
          </select>
        </label>
        <label>
          Status
          <select value={filters.status} onChange={(event) => setFilter("status", event.target.value)}>
            <option value="">All statuses</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>
        <button type="button" className="secondary-button" onClick={resetFilters}>
          Reset Filters
        </button>
      </div>
      <p className="active-filters">{activeSummary}</p>
    </section>
  );
}
