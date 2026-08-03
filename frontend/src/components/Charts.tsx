import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend, Cell } from "recharts";

interface ChartTooltipProps {
  active?: boolean;
  payload?: Array<{ value: number; name: string; color?: string; dataKey?: string }>;
  label?: string;
}

export function CustomTooltip({ active, payload, label }: ChartTooltipProps) {
  if (!active || !payload) return null;

  return (
    <div className="custom-tooltip">
      <p className="tooltip-label">{label}</p>
      {payload.map((entry, index) => (
        <p key={index} className="tooltip-item" style={{ color: entry.color || "#2563eb" }}>
          {entry.name}: <strong>{entry.value}</strong>
        </p>
      ))}
    </div>
  );
}

interface BarChartEnhancedProps {
  data: Array<{ name: string; value: number }>;
  title?: string;
  color?: string;
  height?: number;
  showLegend?: boolean;
}

export function BarChartEnhanced({ data, title, color = "#2563eb", height = 260, showLegend = false }: BarChartEnhancedProps) {
  return (
    <article className="panel chart-panel">
      {title && (
        <div className="panel-heading">
          <h3>{title}</h3>
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
          <XAxis type="number" tick={{ fontSize: 11 }} />
          <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={160} />
          <Tooltip content={<CustomTooltip />} />
          {showLegend && <Legend />}
          <Bar dataKey="value" fill={color} radius={[0, 4, 4, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.value > 80 ? "#ef4444" : color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </article>
  );
}

interface LineChartEnhancedProps {
  data: Array<{ name: string; value: number }>;
  title?: string;
  color?: string;
  height?: number;
  yDomain?: [number, number];
  showDots?: boolean;
}

export function LineChartEnhanced({ data, title, color = "#0f88a8", height = 260, yDomain, showDots = false }: LineChartEnhancedProps) {
  return (
    <article className="panel chart-panel">
      {title && (
        <div className="panel-heading">
          <h3>{title}</h3>
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
          <XAxis dataKey="name" tick={{ fontSize: 11 }} />
          <YAxis domain={yDomain || "auto"} tick={{ fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={3} dot={showDots} />
        </LineChart>
      </ResponsiveContainer>
    </article>
  );
}

interface MultiLineChartProps {
  data: Array<Record<string, any>>;
  lines: Array<{ dataKey: string; color: string; name: string }>;
  title?: string;
  height?: number;
  xKey?: string;
}

export function MultiLineChart({ data, lines, title, height = 260, xKey = "name" }: MultiLineChartProps) {
  return (
    <article className="panel chart-panel">
      {title && (
        <div className="panel-heading">
          <h3>{title}</h3>
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
          <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          {lines.map((line) => (
            <Line key={line.dataKey} type="monotone" dataKey={line.dataKey} stroke={line.color} strokeWidth={2} name={line.name} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </article>
  );
}

export function DonutChart({ data, title, colors = ["#2563eb", "#0f88a8", "#10b981", "#f59e0b", "#ef4444"] }: {
  data: Array<{ name: string; value: number }>;
  title?: string;
  colors?: string[];
}) {
  return (
    <article className="panel chart-panel">
      {title && (
        <div className="panel-heading">
          <h3>{title}</h3>
        </div>
      )}
      <div style={{ height: 260, display: "flex", justifyContent: "center" }}>
        <ResponsiveContainer width="80%" height="100%">
          <BarChart data={data} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis type="number" tick={{ fontSize: 11 }} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={160} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="value" fill={colors[0]} radius={[0, 4, 4, 0]}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}