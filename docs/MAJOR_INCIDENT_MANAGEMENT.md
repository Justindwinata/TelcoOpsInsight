# Major Incident Management

ITIL-inspired Major Incident (MI) workflow for high-impact service disruptions.

## Workflow Stages

1. **Declaration** - MI declared by NOC/Management
2. **War Room** - Incident commander assigned, war room activated
3. **Impact Analysis** - Services, regions, customers affected
4. **Resolution** - Fix implemented, service restored
5. **Post-Incident Review** - PIR document with root cause, lessons learned

## Key Features

- Incident Commander assignment
- Stakeholder notification list
- Timeline of events
- Resolution tracking
- PIR documentation

## API Endpoints

- `GET /api/major-incidents` - List MIs
- `POST /api/major-incidents` - Create MI
- `GET /api/major-incidents/{id}` - MI details
- `PUT /api/major-incidents/{id}/status` - Update status
- `POST /api/major-incidents/{id}/stakeholders` - Add stakeholder
- `GET /api/major-incidents/{id}/timeline` - Event timeline
- `POST /api/major-incidents/{id}/resolve` - Close with PIR
