import { useEffect, useMemo, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { CollapsibleWidget } from "../components/CollapsibleWidget";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import { integerValue, numberValue, percentageValue } from "../utils/format";

interface KpiScorecard {
  name: string;
  value: number;
  target: number;
  trend: number;
  status: "Met" | "Approaching" | "At Risk" | "Critical";
}

interface ExecutiveScorecardResponse {
  kpis: KpiScorecard[];
  trend_data: Array<{ name: string; value: number }>;
  summary: {
    overall_score: number;
    improvement_count: number;
    at_risk_count: number;
  };
}

export function ExecutiveScorecards() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<ExecutiveScorecardResponse>(`/api/dashboard/scorecards${queryString}`);

  if (loading) return <LoadingState label="Loading executive scorecards" />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Met": return "healthy";
      case "Approaching": return "neutral";
      case "At Risk": return "warning";
      case "Critical": return "critical";
      default: return "neutral";
    }
  };

  return (
    <div className="grid">
      <section className="kpi-grid">
        {data.kpis.map((kpi, index) => (
          <KpiCard
            key={index}
            label={kpi.name}
            value={percentageValue(kpi.value)}
            tone={getStatusColor(kpi.status)}
          />
        ))}
      </section>

      <section className="grid two">
        <CollapsibleWidget title="Scorecard Status">
          <div className="status-grid">
            {data.kpis.map((kpi, index) => (
              <div key={index} className="status-card">
                <strong>{kpi.name}</strong>
                <span className={`badge tone-${kpi.status.toLowerCase()}`}>{kpi.status}</span>
                <p>Target: {percentageValue(kpi.target)} | Trend: {numberValue(kpi.trend, 1)}%</p>
              </div>
            ))}
          </div>
        </CollapsibleWidget>

        <CollapsibleWidget title="Overall Summary">
          <dl className="metric-list">
            <div>
              <dt>Overall Score</dt>
              <dd>{numberValue(data.summary.overall_score)}</dd>
            </div>
            <div>
              <dt>Improving KPIs</dt>
              <dd>{integerValue(data.summary.improvement_count)}</dd>
            </div>
            <div>
              <dt>At Risk KPIs</dt>
              <dd>{integerValue(data.summary.at_risk_count)}</dd>
            </div>
          </dl>
        </CollapsibleWidget>
      </section>

      <CollapsibleWidget title="Trend Analysis">
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data.trend_data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4ebf2" />
            <XAxis dataKey="name" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} />
            <Tooltip formatter={(value) => [`${value}%`, "Score"]} />
            <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </CollapsibleWidget>
    </div>
  );
}
