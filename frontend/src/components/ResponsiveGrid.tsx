import { useMemo } from "react";

type GridProps = {
  children: React.ReactNode;
  columns?: "1" | "2" | "3" | "auto";
  className?: string;
};

export function ResponsiveGrid({ children, columns = "auto", className = "" }: GridProps) {
  const gridClass = useMemo(() => {
    if (columns === "1") return "grid responsive-1col";
    if (columns === "2") return "grid responsive-2col";
    if (columns === "3") return "grid responsive-3col";
    return "grid responsive-auto";
  }, [columns]);

  return <div className={`${gridClass} ${className}`}>{children}</div>;
}

export function ResponsiveTable({ children }: { children: React.ReactNode }) {
  return (
    <div className="responsive-table-container">
      {children}
    </div>
  );
}

export function ResponsiveChart({ children }: { children: React.ReactNode }) {
  return (
    <div className="responsive-chart-container">
      {children}
    </div>
  );
}
