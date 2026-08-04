import type { ReactNode } from "react";

interface MetricListItem {
  label: string;
  value: string | number;
}

interface MetricListProps {
  items: MetricListItem[];
}

export function MetricList({ items }: MetricListProps) {
  return (
    <dl className="metric-list">
      {items.map((item, index) => (
        <div key={index}>
          <dt>{item.label}</dt>
          <dd>{item.value}</dd>
        </div>
      ))}
    </dl>
  );
}

interface DataTableProps<T> {
  columns: Array<{ key: string; label: string; render?: (row: T) => string | number }>;
  data: T[];
  emptyMessage?: string;
  maxRows?: number;
}

export function DataTable<T extends Record<string, any>>({ columns, data, emptyMessage = "No data", maxRows = 20 }: DataTableProps<T>) {
  const displayData = data.slice(0, maxRows);

  if (data.length === 0) {
    return <div className="empty-state">{emptyMessage}</div>;
  }

  return (
    <div className="table-wrap compact-table">
      <table>
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={col.key}>{col.render ? col.render(row) : String(row[col.key] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

interface PanelProps {
  title: string;
  badge?: string | number;
  children: ReactNode;
}

export function Panel({ title, badge, children }: PanelProps) {
  return (
    <article className="panel">
      <div className="panel-heading">
        <h3>{title}</h3>
        {badge !== undefined && <span className="badge">{badge}</span>}
      </div>
      {children}
    </article>
  );
}

interface KpiGridProps {
  items: Array<{
    label: string;
    value: string | number;
    tone?: "healthy" | "warning" | "critical" | "neutral";
  }>;
}

export function KpiGrid({ items }: KpiGridProps) {
  return (
    <section className="kpi-grid">
      {items.map((item, index) => (
        <div key={index} className={`kpi-card tone-${item.tone || "neutral"}`}>
          <div className="kpi-label">{item.label}</div>
          <div className="kpi-value">{item.value}</div>
        </div>
      ))}
    </section>
  );
}
