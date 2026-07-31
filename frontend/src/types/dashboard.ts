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
