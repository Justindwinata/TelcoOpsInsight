import { useState } from "react";

export function PrintMode({ children }: { children: React.ReactNode }) {
  const [inPrintMode, setInPrintMode] = useState(false);

  const togglePrintMode = () => {
    setInPrintMode(!inPrintMode);
    if (!inPrintMode) {
      setTimeout(() => window.print(), 100);
    }
  };

  return (
    <div className={inPrintMode ? "print-mode" : ""}>
      <button onClick={togglePrintMode} style={{ padding: "4px 12px", borderRadius: 4, cursor: "pointer" }}>
        {inPrintMode ? "Exit Print Mode" : "Print Report"}
      </button>
      {children}
    </div>
  );
}
