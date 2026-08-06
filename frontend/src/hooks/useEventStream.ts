import { useEffect, useRef, useState, useCallback } from "react";

export type StreamEvent = {
  event_id: string;
  event_type: string;
  severity: string;
  title: string;
  detail: string;
  region: string;
  service_type: string;
  site_id: string;
  acknowledged: boolean;
  resolved: boolean;
  timestamp: string;
};

type StreamStatus = "connecting" | "connected" | "disconnected" | "paused";

export function useEventStream(enabled = true) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<StreamStatus>("disconnected");
  const [connectionInfo, setConnectionInfo] = useState({
    connectedAt: null as Date | null,
    lastUpdate: null as Date | null,
    eventRate: 0,
    totalEvents: 0,
  });
  const eventSourceRef = useRef<EventSource | null>(null);
  const eventCountRef = useRef(0);
  const lastUpdateRef = useRef<Date | null>(null);
  const pausedRef = useRef(false);

  const clearFeed = useCallback(() => {
    setEvents([]);
    eventCountRef.current = 0;
  }, []);

  const pauseStream = useCallback(() => {
    pausedRef.current = true;
    setStatus((s) => (s === "connected" ? "paused" : s));
  }, []);

  const resumeStream = useCallback(() => {
    pausedRef.current = false;
    if (eventSourceRef.current) setStatus("connected");
  }, []);

  useEffect(() => {
    if (!enabled) {
      eventSourceRef.current?.close();
      eventSourceRef.current = null;
      setStatus("disconnected");
      return;
    }

    const token = localStorage.getItem("telcoops_auth_token");
    const es = new EventSource(`/api/events/stream?token=${token}`);
    eventSourceRef.current = es;

    es.onopen = () => setStatus("connected");
    es.onerror = () => setStatus("disconnected");

    es.addEventListener("event", (msg) => {
      if (pausedRef.current) return;
      try {
        const event = JSON.parse((msg as MessageEvent).data) as StreamEvent;
        setEvents((prev) => [event, ...prev].slice(0, 500));
        eventCountRef.current += 1;
        const now = new Date();
        lastUpdateRef.current = now;
        setConnectionInfo((info) => ({
          ...info,
          lastUpdate: now,
          eventRate: info.eventRate,
          totalEvents: eventCountRef.current,
        }));
      } catch {
        // ignore malformed events
      }
    });

    es.addEventListener("heartbeat", () => {
      lastUpdateRef.current = new Date();
      setConnectionInfo((info) => ({ ...info, lastUpdate: new Date() }));
    });

    es.addEventListener("connected", () => {
      setStatus("connected");
    });

    // Reset event rate tracking every 10s
    const rateInterval = setInterval(() => {
      setConnectionInfo((info) => ({ ...info, eventRate: 0 }));
    }, 10000);

    return () => {
      es.close();
      eventSourceRef.current = null;
      clearInterval(rateInterval);
      setStatus("disconnected");
    };
  }, [enabled]);

  return {
    events,
    status,
    connectionInfo,
    connectStream: () => {
      // reconnections handled by EventSource automatically
    },
    disconnectStream: () => {
      eventSourceRef.current?.close();
      eventSourceRef.current = null;
      setStatus("disconnected");
    },
    pauseStream,
    resumeStream,
    clearFeed,
  };
}