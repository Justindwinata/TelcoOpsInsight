const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const TOKEN_KEY = "telcoops_auth_token";
const USER_KEY = "telcoops_auth_user";

export type AuthUser = {
  username: string;
  display_name: string;
  role: string;
  permissions: string[];
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getStoredUser(): AuthUser | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) {
    return null;
  }
  try {
    return JSON.parse(raw) as AuthUser;
  } catch {
    return null;
  }
}

export function storeAuth(payload: LoginResponse) {
  localStorage.setItem(TOKEN_KEY, payload.access_token);
  localStorage.setItem(USER_KEY, JSON.stringify(payload.user));
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function authHeaders(): HeadersInit {
  const token = getStoredToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function parseError(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    return typeof payload.detail === "string" ? payload.detail : `API request failed: ${response.status}`;
  } catch {
    return `API request failed: ${response.status}`;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    if (response.status === 401) {
      clearAuth();
    }
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  return handleResponse<T>(response);
}

export async function apiGetText(path: string): Promise<string> {
  const response = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  if (!response.ok) {
    if (response.status === 401) {
      clearAuth();
    }
    throw new Error(await parseError(response));
  }
  return response.text();
}

export async function apiPost<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { method: "POST", headers: authHeaders() });
  return handleResponse<T>(response);
}

export async function apiJsonPost<T>(path: string, body: object): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearAuth();
    }
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<T>;
}

export async function loginRequest(username: string, password: string): Promise<LoginResponse> {
  const payload = await apiJsonPost<LoginResponse>("/api/auth/login", { username, password });
  storeAuth(payload);
  return payload;
}

export async function logoutRequest(): Promise<void> {
  try {
    await apiPost("/api/auth/logout");
  } finally {
    clearAuth();
  }
}

export async function uploadCsv<T>(file: File, persist = false): Promise<T> {
  const formData = new FormData();
  formData.append("file", file);
  const response = await fetch(`${API_BASE}/api/datasets/upload?persist=${persist ? "true" : "false"}`, {
    method: "POST",
    headers: authHeaders(),
    body: formData
  });
  if (!response.ok) {
    if (response.status === 401) {
      clearAuth();
    }
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<T>;
}
