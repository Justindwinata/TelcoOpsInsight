# Change Management

ITIL Change Advisory Board (CAB) workflow for controlled infrastructure changes.

## Change Types

- **Planned Change** - Scheduled, assessed risk
- **Emergency Change** - Urgent, expedited approval
- **Standard Change** - Pre-approved, low risk

## Workflow

1. **RFC Creation** - Request for Change submitted
2. **Assessment** - Risk level, impact, rollback plan
3. **CAB Review** - Approval/Rejection
4. **Scheduling** - Maintenance window allocation
5. **Implementation** - Execute with monitoring
6. **Post-Implementation Review** - Verify success

## API Endpoints

- `GET /api/changes` - List changes (existing)
- `POST /api/changes` - Create RFC
- `PUT /api/changes/{id}` - Update status
