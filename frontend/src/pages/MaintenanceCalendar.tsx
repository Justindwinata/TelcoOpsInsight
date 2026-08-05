import { useApi } from "../hooks/useApi";
import { LoadingState, ErrorState, EmptyState } from "../components/StateViews";

type CalendarEvent = {
  event_id: string;
  event_type: string;
  title: string;
  date: string;
  status: string;
  region: string;
};

export function MaintenanceCalendar() {
  const data = useApi<{ events: CalendarEvent[]; upcoming: CalendarEvent[] }>("/api/calendar");
  if (data.loading) return <LoadingState label="Loading calendar" />;
  if (data.error) return <ErrorState message={data.error} />;
  if (!data.data) return <EmptyState />;
  
  return (
    <div className="grid">
      <article className="panel">
        <div className="panel-heading"><h3>Upcoming Activities</h3></div>
        {data.data.upcoming.length > 0 ? (
          <div className="table-wrap">
            <table>
              <thead><tr><th>Date</th><th>Type</th><th>Title</th><th>Region</th><th>Status</th></tr></thead>
              <tbody>
                {data.data.upcoming.map((e) => (
                  <tr key={e.event_id}>
                    <td>{e.date}</td>
                    <td><span className="badge">{e.event_type}</span></td>
                    <td>{e.title}</td>
                    <td>{e.region}</td>
                    <td>{e.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <EmptyState message="No upcoming activities" />}
      </article>
    </div>
  );
}
