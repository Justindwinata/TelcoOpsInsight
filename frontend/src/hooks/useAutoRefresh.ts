import { useState, useEffect, useCallback } from "react";

export function useAutoRefresh(refreshInterval: number, callback: () => void, enabled: boolean = true) {
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const refresh = useCallback(() => {
    callback();
    setLastRefresh(new Date());
  }, [callback]);

  useEffect(() => {
    if (!enabled || refreshInterval <= 0) return;
    const interval = setInterval(refresh, refreshInterval * 1000);
    return () => clearInterval(interval);
  }, [refresh, refreshInterval, enabled]);

  return { lastRefresh, refresh };
}
