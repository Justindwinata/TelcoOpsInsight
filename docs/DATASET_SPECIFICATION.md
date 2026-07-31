# Dataset Specification

All files under `datasets/sample/` are synthetic and deterministic. The sample period is `2026-01-01` through `2026-12-31`.

## Enumerations

Regions: Jakarta, Bandung, Surabaya, Medan, Makassar, Semarang, Yogyakarta, Denpasar, Palembang, Balikpapan.

Service types: Fiber Internet, Mobile Broadband, Enterprise VPN, IPTV, Voice, Cloud Connectivity.

Severity and priority: Low, Medium, High, Critical.

Incident status: Open, Investigating, Escalated, Resolved, Closed.

Ticket status: Open, In Progress, Waiting Customer, Resolved, Closed.

Operational teams: NOC Core, Field Operations, Customer Assurance, Fiber Maintenance, Enterprise Support.

## Required Files

### network_sites.csv

Columns: `site_id`, `site_name`, `region`, `city`, `service_type`, `site_type`, `capacity_mbps`, `active_customers`, `criticality`, `latitude`, `longitude`, `activation_date`.

Validation rules: `site_id` unique, `capacity_mbps > 0`, `active_customers >= 0`, valid region, valid criticality.

### network_incidents.csv

Columns: `incident_id`, `date`, `month`, `site_id`, `region`, `service_type`, `severity`, `status`, `start_time`, `resolved_time`, `duration_minutes`, `affected_customers`, `root_cause`, `assigned_team`, `escalation_level`, `recommended_action`.

Validation rules: `incident_id` unique, `site_id` exists in `network_sites.csv`, valid severity/status, non-negative duration and affected customers, `month` matches `date`, resolved/closed incidents have `resolved_time`, unresolved incidents may have blank `resolved_time`.

### customer_tickets.csv

Columns: `ticket_id`, `date`, `month`, `region`, `service_type`, `ticket_category`, `priority`, `status`, `response_time_minutes`, `resolution_time_minutes`, `related_incident_id`, `customer_segment`, `repeat_complaint`, `satisfaction_score`.

Validation rules: `ticket_id` unique, valid priority/status/category, non-negative response and resolution times, satisfaction between 1 and 5 when present, related incident ID exists when provided.

### sla_metrics.csv

Columns: `date`, `month`, `region`, `service_type`, `sla_target`, `sla_actual`, `uptime_percentage`, `downtime_minutes`, `mttr_minutes`, `breach_count`, `availability_score`.

Validation rules: percentages between 0 and 100, non-negative downtime and MTTR, non-negative breach count, SLA target usually between 95 and 99.9.

### field_technician_jobs.csv

Columns: `job_id`, `date`, `month`, `technician_id`, `technician_name`, `region`, `assigned_team`, `job_type`, `status`, `priority`, `dispatch_time_minutes`, `completion_time_minutes`, `first_time_fix`, `related_incident_id`.

Validation rules: `job_id` unique, non-negative dispatch/completion times, boolean first-time fix value, related incident ID exists when provided.

### region_performance.csv

Columns: `date`, `month`, `region`, `total_sites`, `active_incidents`, `critical_incidents`, `open_tickets`, `affected_customers`, `sla_achievement`, `avg_latency_ms`, `packet_loss_rate`, `technician_utilization`, `customer_satisfaction`.

Validation rules: `total_sites > 0`, operational counts non-negative, percentages between 0 and 100, satisfaction between 1 and 5.

### service_quality_metrics.csv

Columns: `timestamp`, `date`, `month`, `region`, `site_id`, `service_type`, `latency_ms`, `packet_loss_rate`, `jitter_ms`, `bandwidth_utilization`, `availability_percentage`, `quality_score`.

Validation rules: `site_id` exists in `network_sites.csv`, numeric values non-negative, percentage fields between 0 and 100, quality score between 0 and 100.

### recommendation_rules.csv

Columns: `rule_id`, `metric`, `condition`, `threshold`, `severity`, `recommendation_title`, `recommendation_text`, `recommended_owner`.

Validation rules: `rule_id` unique, valid severity, non-empty recommendation text.

### telco_ops_sample_bundle.json

JSON summary containing generated file names, row counts, period, regions, services, and synthetic-data disclaimer.
