import { EmptyState, ErrorState, LoadingState } from "../components/StateViews";
import { useDashboardFilters } from "../filters/FilterContext";
import { useApi } from "../hooks/useApi";
import type { RecommendationsResponse } from "../types/dashboard";
import { integerValue, numberValue } from "../utils/format";

export function Recommendations() {
  const { queryString } = useDashboardFilters();
  const { data, loading, error } = useApi<RecommendationsResponse>(`/api/dashboard/recommendations${queryString}`);

  if (loading) {
    return <LoadingState label="Loading recommendations" />;
  }
  if (error) {
    return <ErrorState message={error} />;
  }
  if (!data) {
    return <EmptyState />;
  }

  return (
    <div className="grid">
      <section className="panel">
        <div className="panel-heading">
          <h3>Rule-Based Operational Recommendations</h3>
          <span className="badge">
            {integerValue(data.triggered_count)} triggered / {integerValue(data.rules_evaluated)} rules
          </span>
        </div>
        <div className="recommendation-grid">
          {data.recommendations.map((item) => (
            <article className="recommendation-item" key={item.rule_id}>
              <div className="recommendation-topline">
                <span className={`severity ${item.severity.toLowerCase()}`}>{item.severity}</span>
                <span className="muted">{item.region}</span>
              </div>
              <strong>{item.recommendation_title}</strong>
              <p>{item.recommendation_text}</p>
              <dl className="inline-metrics">
                <div>
                  <dt>Observed</dt>
                  <dd>{numberValue(item.observed_value, 2)}</dd>
                </div>
                <div>
                  <dt>Rule</dt>
                  <dd>
                    {item.condition} {numberValue(item.threshold, 2)}
                  </dd>
                </div>
                <div>
                  <dt>Owner</dt>
                  <dd>{item.recommended_owner}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
        {data.recommendations.length === 0 ? <EmptyState message="No active recommendation rules are triggered." /> : null}
      </section>
    </div>
  );
}
