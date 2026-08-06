import { useState, useCallback, createContext, useContext, type ReactNode } from "react";

type NotificationType = "success" | "error" | "warning" | "info";
type Notification = { id: string; type: NotificationType; message: string; timestamp: number };

interface NotificationContextType {
  notifications: Notification[];
  notify: (type: NotificationType, message: string) => void;
  dismiss: (id: string) => void;
}

const NotificationContext = createContext<NotificationContextType>({
  notifications: [],
  notify: () => {},
  dismiss: () => {},
});

export function useNotifications() {
  return useContext(NotificationContext);
}

export function NotificationProvider({ children }: { children: ReactNode }) {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const notify = useCallback((type: NotificationType, message: string) => {
    const id = `notif-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setNotifications((prev) => [...prev, { id, type, message, timestamp: Date.now() }]);
    setTimeout(() => dismiss(id), 5000);
  }, []);

  const dismiss = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, notify, dismiss }}>
      {children}
      <div className="notification-stack" style={{ position: "fixed", top: 16, right: 16, zIndex: 9999, display: "flex", flexDirection: "column", gap: 8, maxWidth: 400 }}>
        {notifications.map((n) => (
          <div key={n.id} className={`notification-toast ${n.type}`} style={{
            padding: "12px 16px", borderRadius: 6, background: n.type === "error" ? "#fef2f2" : n.type === "success" ? "#f0fdf4" : n.type === "warning" ? "#fffbeb" : "#eff6ff",
            border: `1px solid ${n.type === "error" ? "#fecaca" : n.type === "success" ? "#bbf7d0" : n.type === "warning" ? "#fde68a" : "#bfdbfe"}`,
            color: "#1e293b", fontSize: 13, display: "flex", justifyContent: "space-between", alignItems: "center", boxShadow: "0 4px 12px rgba(0,0,0,0.1)", cursor: "pointer",
          }} onClick={() => dismiss(n.id)}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 16 }}>{n.type === "error" ? "❌" : n.type === "success" ? "✅" : n.type === "warning" ? "⚠️" : "ℹ️"}</span>
              {n.message}
            </div>
            <button type="button" onClick={(e) => { e.stopPropagation(); dismiss(n.id); }} style={{ border: "none", background: "none", cursor: "pointer", fontSize: 14, color: "#64748b" }}>✕</button>
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  );
}
