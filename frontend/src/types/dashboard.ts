export type NamedValue = {
  name: string;
  value: number;
};

export type OverviewMetrics = {
  total_sites: number;
  active_incidents: number;
  critical_incidents: number;
  resolved_incidents: number;
  average_mttr_minutes: number;
  network_uptime: number;
  sla_achievement: number;
  sla_breach_count: number;
  average_latency_ms: number;
  packet_loss_rate: number;
  high_packet_loss_regions: string[];
  open_ticket_backlog: number;
  repeat_complaint_rate: number;
  technician_utilization: number;
  first_time_fix_rate: number;
  field_job_completion_time_minutes: number;
  affected_customers: number;
  customer_satisfaction: number;
};

export type Recommendation = {
  rule_id: string;
  severity: string;
  metric: string;
  condition: string;
  threshold: number;
  observed_value: number;
  recommendation_title: string;
  recommendation_text: string;
  recommended_owner: string;
  region: string;
};

export type NetworkHealthResponse = {
  uptime_trend: NamedValue[];
  latency_trend: NamedValue[];
  packet_loss_trend: NamedValue[];
  service_quality_summary: NamedValue[];
};

export type RecommendationsResponse = {
  recommendations: Recommendation[];
  triggered_count: number;
  rules_evaluated: number;
  method: string;
};

export type Incident = {
  incident_id: string;
  date: string;
  region: string;
  service_type: string;
  severity: string;
  status: string;
  duration_minutes: string;
  affected_customers: string;
  root_cause: string;
  assigned_team: string;
};

export type IncidentsResponse = {
  incidents: Incident[];
  severity_summary: NamedValue[];
  incident_trend: NamedValue[];
  root_cause_breakdown: NamedValue[];
  top_root_causes: NamedValue[];
};

export type TicketsResponse = {
  ticket_volume: NamedValue[];
  backlog: number;
  category_breakdown: NamedValue[];
  response_time_summary: { average_minutes: number };
  resolution_time_summary: { average_minutes: number };
  customer_segment_summary: NamedValue[];
  repeat_complaint_rate: number;
};

export type SlaPoint = {
  name: string;
  target: number;
  actual: number;
};

export type SlaComparison = {
  region: string;
  service_type: string;
  sla_target: number;
  sla_actual: number;
  breach_count: number;
};

export type SlaResponse = {
  target_vs_actual: SlaPoint[];
  breach_count: number;
  region_service_comparison: SlaComparison[];
  mttr_trend: NamedValue[];
};

export type TechniciansResponse = {
  technician_workload: NamedValue[];
  dispatch_time: { average_minutes: number };
  completion_time: { average_minutes: number };
  first_time_fix_rate: number;
  job_status_summary: NamedValue[];
};
