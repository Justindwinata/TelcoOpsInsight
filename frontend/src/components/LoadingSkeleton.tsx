export function LoadingSkeleton({ rows = 5, columns = 4 }: { rows?: number; columns?: number }) {
  return (
    <div className="skeleton-loader">
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton-row" style={{ display: "flex", gap: 8, marginBottom: 8 }}>
          {Array.from({ length: columns }).map((_, j) => (
            <div key={j} className="skeleton-cell" style={{
              height: 14,
              flex: 1,
              background: "#e4ebf2",
              borderRadius: 4,
              animation: "pulse 1.5s ease-in-out infinite",
            }} />
          ))}
        </div>
      ))}
    </div>
  );
}
