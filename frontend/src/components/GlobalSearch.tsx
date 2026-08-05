import { useState } from "react";

export function GlobalSearch({ onSearch }: { onSearch: (query: string) => void }) {
  const [query, setQuery] = useState("");

  return (
    <div className="global-search">
      <input
        type="text"
        placeholder="Search incidents, alarms, technicians, service requests..."
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          onSearch(e.target.value);
        }}
        style={{ width: "100%", padding: "8px 12px", borderRadius: 4, border: "1px solid #e4ebf2" }}
      />
    </div>
  );
}
