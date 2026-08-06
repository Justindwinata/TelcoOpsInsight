import { useEffect, useRef } from "react";
import { useNotifications } from "../components/NotificationManager";
import type { StreamEvent } from "./useEventStream";

const NOTIFY_SEVERITIES = ["Critical", "Major"];

export function useLiveNotifications(events: StreamEvent[], enabled = true) {
  const { notify } = useNotifications();
  const seenIds = useRef<Set<string>>(new Set());

  useEffect(() => {
    if (!enabled || events.length === 0) return;

    events.forEach((event) => {
      if (!NOTIFY_SEVERITIES.includes(event.severity)) return;
      if (seenIds.current.has(event.event_id)) return;

      seenIds.current.add(event.event_id);
      const type = event.severity === "Critical" ? "error" : "warning";
      notify(type, `${event.severity}: ${event.title} (${event.region})`);
    });
  }, [events, enabled, notify]);

  return { notify };
}