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
  priority_score: number;
  confidence: string;
  business_impact: string;
  expected_impact: string;
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
  scoring?: {
    model: string;
    description: string;
  };
};

export type Notification = {
  id: string;
  category: string;
  severity: string;
  title: string;
  message: string;
  count: number;
  action_url: string;
  action_label: string;
};

export type NotificationsResponse = {
  notifications: Notification[];
  total_count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  categories: string[];
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

export type AssetInventoryResponse = {
  total_assets: number;
  asset_types: NamedValue[];
  asset_statuses: NamedValue[];
  ownership: NamedValue[];
  region_distribution: NamedValue[];
  active_count: number;
  faulty_count: number;
  maintenance_count: number;
  faulty_assets: Array<Record<string, string | number>>;
  status_breakdown: Record<string, number>;
  type_breakdown: Record<string, number>;
  warranty_expiring: Array<Record<string, string>>;
  due_maintenance: Array<Record<string, string>>;
  health_score: number;
};

export type AssetDetailResponse = {
  assets: Array<Record<string, string>>;
  total: number;
};

export type MaintenanceJob = {
  job_id?: string;
  date: string;
  region: string;
  technician_id?: string;
  assigned_team?: string;
  job_type: string;
  priority?: string;
  status: string;
  related_incident_id?: string;
  completion_time_minutes?: string;
  first_time_fix?: string;
};

export type MaintenanceResponse = {
  total_jobs: number;
  preventive_count: number;
  corrective_count: number;
  installation_count: number;
  audit_count: number;
  upcoming_count: number;
  in_progress_count: number;
  completed_count: number;
  avg_completion_time_minutes: number;
  avg_dispatch_time_minutes: number;
  first_time_fix_rate: number;
  job_type_breakdown: Record<string, number>;
  status_breakdown: Record<string, number>;
  by_region: NamedValue[];
  by_team: NamedValue[];
  by_priority: NamedValue[];
  upcoming_jobs: MaintenanceJob[];
  completed_jobs: MaintenanceJob[];
  asset_maintenance_due: Array<Record<string, string>>;
};

export type ChangeRecord = {
  change_id: string;
  title: string;
  change_type: string;
  risk_level: string;
  status: string;
  region: string;
  service_type: string;
  requester: string;
  approver: string | null;
  description: string;
  rollback_plan: string;
  scheduled_start: string;
  scheduled_end: string;
  actual_start: string;
  actual_end: string;
  related_incident_id: string;
  affected_sites: string;
  created_at: string;
  updated_at: string;
};

export type ChangeSummaryResponse = {
  total_changes: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  by_risk: Record<string, number>;
  by_region: Record<string, number>;
  pending_approval: number;
  approved: number;
  in_progress: number;
  completed: number;
  rolled_back: number;
  failed: number;
  approval_rate: number;
  rollback_rate: number;
  failure_rate: number;
  recent_changes: ChangeRecord[];
  statuses: string[];
  types: string[];
  risk_levels: string[];
};

export type RcaSummaryResponse = {
  total_rcas: number;
  by_status: Record<string, number>;
  by_category: Record<string, number>;
  by_method: Record<string, number>;
  by_severity: Record<string, number>;
  implemented: number;
  closed: number;
  in_review: number;
  statuses: string[];
  categories: string[];
  methods: string[];
};

export type TimelineEvent = {
  timestamp: string;
  event: string;
  title: string;
  detail: string;
  actor: string;
};

export type IncidentTimelineEntry = {
  incident_id: string;
  date: string;
  severity: string;
  status: string;
  region: string;
  service_type: string;
  assigned_team: string;
  escalation_level: string;
  root_cause: string;
  affected_customers: string;
  duration_minutes: string;
  start_time: string;
  resolved_time: string;
  event_count: number;
  events: TimelineEvent[];
};

export type IncidentTimelinesResponse = {
  total_incidents: number;
  with_escalation: number;
  resolved: number;
  closed: number;
  average_events_per_incident: number;
  timelines: IncidentTimelineEntry[];
  incidents: Array<Record<string, string>>;
};
