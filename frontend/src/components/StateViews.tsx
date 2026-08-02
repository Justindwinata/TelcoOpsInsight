export function LoadingState({ label = "Loading data" }: { label?: string }) {
  return (
    <section className="state loading-state">
      <div className="state-spinner"></div>
      <p>{label}...</p>
    </section>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <section className="state error-state">
      <div className="state-icon">⚠️</div>
      <strong>Error</strong>
      <p>{message}</p>
    </section>
  );
}

export function EmptyState({ message = "No records available for the selected view." }: { message?: string }) {
  return (
    <section className="state empty-state">
      <div className="state-icon">📭</div>
      <p>{message}</p>
    </section>
  );
}
