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
