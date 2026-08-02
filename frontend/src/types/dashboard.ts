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
  supporting_metric_value: number;
  trigger_condition: string;
  affected_region: string;
  affected_service: string;
  recommendation_title: string;
  recommendation_text: string;
  explanation: string;
  recommended_action: string;
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

export type IncidentDrilldownResponse = {
  by_severity: NamedValue[];
  by_root_cause: NamedValue[];
  by_region: NamedValue[];
  active_by_region: NamedValue[];
  critical_incidents: Incident[];
};

export type IncidentLifecycleStage = {
  stage: string;
  label: string;
  count: number;
  percentage: number;
};

export type IncidentLifecycleResponse = {
  lifecycle_stages: IncidentLifecycleStage[];
  total_incidents: number;
  active_count: number;
  resolved_count: number;
  average_duration_active_minutes: number;
  average_duration_resolved_minutes: number;
  active_severity_breakdown: Record<string, number>;
  oldest_active: Array<Record<string, string | number>>;
  stage_progression: Array<{ stage: string; label: string; description: string }>;
};

export type OutageImpactItem = {
  region?: string;
  service_type?: string;
  active_incidents: number;
  affected_customers: number;
  services_impacted?: number;
  regions_impacted?: number;
  impact_score: number;
};

export type OutageImpactResponse = {
  total_active_incidents: number;
  total_affected_customers: number;
  avg_affected_per_incident: number;
  severity_breakdown: Record<string, number>;
  region_impact: OutageImpactItem[];
  service_impact: OutageImpactItem[];
  worst_case_region: OutageImpactItem | null;
  worst_case_service: OutageImpactItem | null;
  multi_region_incidents: number;
  multi_service_incidents: number;
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

export type TicketDrilldownResponse = {
  backlog_by_region: NamedValue[];
  backlog_by_service: NamedValue[];
  category_detail: NamedValue[];
  repeat_complaint_detail: Array<Record<string, string>>;
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

export type SlaBreachDetail = {
  date: string;
  region: string;
  service_type: string;
  sla_target: number;
  sla_actual: number;
  gap: number;
  mttr_minutes: number;
};

export type SlaDrilldownResponse = {
  breach_detail: SlaBreachDetail[];
  breaches_by_region: NamedValue[];
  breaches_by_service: NamedValue[];
  mttr_trend: NamedValue[];
};

export type SlaEscalationLevel = {
  level: string;
  label: string;
  count: number;
  percentage: number;
};

export type SlaEscalationResponse = {
  escalation_levels: SlaEscalationLevel[];
  total_sla_records: number;
  breached_records: number;
  breach_rate: number;
  critical_breaches: Array<Record<string, string | number>>;
  affected_regions: NamedValue[];
  affected_services: NamedValue[];
  avg_mttr_minutes: number;
  max_mttr_minutes: number;
  recovery_trend: NamedValue[];
};

export type TechniciansResponse = {
  technician_workload: NamedValue[];
  dispatch_time: { average_minutes: number };
  completion_time: { average_minutes: number };
  first_time_fix_rate: number;
  job_status_summary: NamedValue[];
};

export type TechnicianDrilldownResponse = {
  workload_by_region: NamedValue[];
  workload_by_team: NamedValue[];
  first_time_fix_by_priority: NamedValue[];
  workload_detail: Array<Record<string, string>>;
};

export type TechnicianAssignmentItem = {
  technician_id: string;
  assigned_team: string;
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  capacity_ratio: number;
  avg_completion_minutes: number;
  avg_dispatch_minutes: number;
  first_time_fix_rate: number;
  critical_jobs: number;
  regions: string[];
};

export type TechnicianTeamCapacity = {
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  technicians: number;
  avg_jobs_per_technician: number;
};

export type TechnicianAssignmentResponse = {
  technicians: TechnicianAssignmentItem[];
  team_capacity: TechnicianTeamCapacity[];
  total_technicians: number;
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  overloaded_technicians: TechnicianAssignmentItem[];
  understaffed_teams: TechnicianTeamCapacity[];
};

export type RegionMetric = {
  date: string;
  region: string;
  total_sites: string;
  active_incidents: string;
  critical_incidents: string;
  open_tickets: string;
  affected_customers: string;
  sla_achievement: string;
  avg_latency_ms: string;
  packet_loss_rate: string;
  technician_utilization: string;
  customer_satisfaction: string;
  health_score?: number;
};

export type RegionsResponse = {
  region_performance_ranking: RegionMetric[];
  region_health_metrics: RegionMetric[];
};

export type SeedResponse = {
  seeded: boolean;
  database_path: string;
  row_counts: Record<string, number>;
};

export type UploadValidationResponse = {
  accepted: boolean;
  dataset_type: string | null;
  rows: number;
  errors: string[];
  warnings: string[];
  imported: boolean;
  import_id: string | null;
};

export type ExecutiveReport = {
  title: string;
  company: string;
  synthetic_data_only: boolean;
  period: string;
  overview: OverviewMetrics;
  top_root_causes: NamedValue[];
  top_regions: RegionMetric[];
  recommendations: Recommendation[];
  limitations: string[];
};

export type ImportHistoryEntry = {
  import_id: string;
  filename: string;
  dataset_type: string | null;
  uploaded_at: string;
  row_count: number;
  valid_row_count: number;
  invalid_row_count: number;
  status: string;
  validation_summary: string;
  actor: string | null;
};

export type ImportRollbackResponse = {
  rolled_back: boolean;
  import_id: string;
  dataset_type: string;
  restored_rows: number;
};

export type AuditLogEntry = {
  audit_id: string;
  timestamp: string;
  actor_username: string | null;
  actor_role: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  summary: string;
  status: string;
};

export type AuditLogsResponse = {
  audit_logs: AuditLogEntry[];
  count: number;
};
