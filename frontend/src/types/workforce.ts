export type WorkforceTechnician = {
  technician_id: string;
  name: string;
  employee_id: string;
  region: string;
  assigned_team: string;
  status: string;
  phone: string;
  email: string;
  hire_date: string;
  years_experience: number;
  certifications: string;
  avg_completion_time_minutes: number;
  avg_dispatch_time_minutes: number;
  first_time_fix_rate: number;
  active_jobs: number;
  total_jobs_completed: number;
  utilization_rate: number;
  availability_percentage: number;
  created_at: string;
  updated_at: string;
};

export type WorkforceSkill = {
  skill_id: string;
  technician_id: string;
  skill_name: string;
  skill_level: string;
  certification_id: string;
  acquired_date: string;
  verified: boolean;
  verified_by: string;
  verified_date: string;
};

export type WorkforceCertification = {
  certification_id: string;
  technician_id: string;
  cert_name: string;
  issuing_body: string;
  issued_date: string;
  expiry_date: string;
  status: string;
  renewal_required: boolean;
};

export type WorkforceShift = {
  shift_id: string;
  technician_id: string;
  shift_type: string;
  start_time: string;
  end_time: string;
  shift_date: string;
  region: string;
  capacity_slots: number;
  assigned_jobs: number;
  status: string;
  created_at: string;
};

export type WorkforceLeaveRequest = {
  leave_id: string;
  technician_id: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  days_requested: number;
  reason: string;
  status: string;
  approver_id: string;
  approval_date: string;
  created_at: string;
  updated_at: string;
};

export type WorkforceAssignment = {
  assignment_id: string;
  technician_id: string;
  job_id: string;
  assigned_date: string;
  start_time: string;
  end_time: string;
  status: string;
  priority: string;
  estimated_duration_minutes: number;
  actual_duration_minutes: number;
  completion_notes: string;
  customer_satisfaction_rating: number;
  first_time_fix: boolean;
  created_at: string;
};

export type WorkforceSummaryResponse = {
  total_technicians: number;
  available: number;
  on_job: number;
  on_leave: number;
  off_shift: number;
  pending_leave_requests: number;
  approved_leave_requests: number;
  avg_utilization_rate: number;
  avg_availability_percentage: number;
  technicians_by_region: Array<{ region: string; count: number }>;
  technicians_by_team: Array<{ team: string; count: number }>;
};
