import { useState, useEffect, useCallback, useRef } from "react";

interface UseApiOptions {
  maxRetries?: number;
  retryDelay?: number;
}

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  retry: () => void;
}

export function useApiWithRetry<T>(url: string, options: UseApiOptions = {}): ApiState<T> {
  const { maxRetries = 3, retryDelay = 1000 } = options;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchData = useCallback(async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;
    setLoading(true);
    setError(null);

    let attempt = 0;
    while (attempt <= maxRetries) {
      try {
        const token = localStorage.getItem("telcoops_token");
        const response = await fetch(url, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          signal: controller.signal,
        });

        if (response.status === 401) {
          throw new Error("Authentication required. Please log in.");
        }
        if (response.status === 403) {
          throw new Error("Permission denied. Your role may not have access.");
        }
        if (response.status === 404) {
          throw new Error("The requested resource was not found.");
        }
        if (response.status >= 500 && attempt < maxRetries) {
          throw new Error(`Server error (${response.status})`);
        }
        if (!response.ok) {
          throw new Error(`Request failed: ${response.statusText}`);
        }

        const result = await response.json();
        setData(result);
        setLoading(false);
        return;
      } catch (err) {
        if (controller.signal.aborted) return;
        if (attempt === maxRetries) {
          const errorMessage = err instanceof Error ? err.message : "Unknown error occurred";
          setError(errorMessage);
          setLoading(false);
          return;
        }
        attempt++;
        await new Promise((resolve) => setTimeout(resolve, retryDelay * attempt));
      }
    }
  }, [url, maxRetries, retryDelay]);

  useEffect(() => {
    fetchData();
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [fetchData, retryCount]);

  const retry = useCallback(() => {
    setRetryCount((count) => count + 1);
  }, []);

  return { data, loading, error, retry };
}
