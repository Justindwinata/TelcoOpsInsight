export function LoadingState({ label = "Loading data" }: { label?: string }) {
  return <section className="state">{label}...</section>;
}

export function ErrorState({ message }: { message: string }) {
  return <section className="state error-state">{message}</section>;
}

export function EmptyState({ message = "No records available for the selected view." }: { message?: string }) {
  return <section className="state">{message}</section>;
}
