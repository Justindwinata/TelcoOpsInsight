import { useState, useEffect } from "react";

export function OfflineDetector() {
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setOffline(false);
    const handleOffline = () => setOffline(true);
    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  if (!offline) return null;

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0, zIndex: 10000,
      background: "#dc2626", color: "#fff", padding: "8px 16px",
      textAlign: "center", fontSize: 13, fontWeight: 600,
    }}>
      ⚠️ You are offline. Check your network connection.
      <button onClick={() => window.location.reload()} style={{
        marginLeft: 12, padding: "4px 12px", background: "#fff", color: "#dc2626",
        border: "none", borderRadius: 4, cursor: "pointer", fontWeight: 600,
      }}>
        Retry
      </button>
    </div>
  );
}
EXF
cat > frontend/src/components/RetryAPI.ts << 'EOF'
import { apiGet } from "../api/client";

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

export async function fetchWithRetry<T>(path: string, retries = MAX_RETRIES): Promise<T> {
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await apiGet<T>(path);
    } catch (error) {
      if (attempt === retries) throw error;
      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY_MS * attempt));
    }
  }
  throw new Error("Max retries exceeded");
}
