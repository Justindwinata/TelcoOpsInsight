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
      You are offline. Check your network connection.
      <button onClick={() => window.location.reload()} style={{
        marginLeft: 12, padding: "4px 12px", background: "#fff", color: "#dc2626",
        border: "none", borderRadius: 4, cursor: "pointer", fontWeight: 600,
      }}>
        Retry
      </button>
    </div>
  );
}