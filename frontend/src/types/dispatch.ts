export type WorkOrder = {
  work_order_id: string;
  job_id: string;
  job_type: string;
  priority: string;
  region: string;
  service_type: string;
  site_id: string;
  site_name: string;
  customer_id: string;
  customer_name: string;
  description: string;
  related_incident_id: string;
  required_skills: string;
  estimated_duration_minutes: number;
  scheduled_start: string;
  scheduled_end: string;
  status: string;
  assigned_technician_id: string;
  assigned_team: string;
  dispatch_date: string;
  created_at: string;
  updated_at: string;
};

export type DispatchAssignment = {
  assignment_id: string;
  work_order_id: string;
  technician_id: string;
  dispatch_date: string;
  assigned_by: string;
  assignment_notes: string;
  status: string;
  assigned_at: string;
  acknowledged_at: string;
  started_at: string;
  completed_at: string;
};

export type DispatchRoute = {
  route_id: string;
  work_order_id: string;
  route_json: string;
  distance_km: number;
  estimated_duration_minutes: number;
  eta_timestamp: string;
  actual_duration_minutes: number;
  route_status: string;
  created_at: string;
  updated_at: string;
};

export type DispatchSummaryResponse = {
  total_work_orders: number;
  pending: number;
  assigned: number;
  in_progress: number;
  completed: number;
  cancelled: number;
  critical_priority: number;
  high_priority: number;
  orders_by_region: Array<{ region: string; count: number }>;
  orders_by_priority: Array<{ priority: string; count: number }>;
  orders_by_status: Array<{ status: string; count: number }>;
};

export type TechnicianWorkloadResponse = {
  total_jobs: number;
  active_jobs: number;
  completed_jobs: number;
  utilization_rate: number;
};