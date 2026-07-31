type KpiCardProps = {
  label: string;
  value: string | number;
  tone?: "healthy" | "warning" | "critical" | "neutral";
};

export function KpiCard({ label, value, tone = "neutral" }: KpiCardProps) {
  return (
    <article className={`kpi-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}
