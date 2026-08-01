import { createContext, useContext, useEffect, useMemo, useState } from "react";
import {
  AUTH_CHANGED_EVENT,
  clearAuth,
  getStoredToken,
  getStoredUser,
  loginRequest,
  logoutRequest,
  type AuthUser
} from "../api/client";

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasPermission: (permission: string) => boolean;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());
  const [token, setToken] = useState<string | null>(() => getStoredToken());

  useEffect(() => {
    function syncAuthState() {
      setUser(getStoredUser());
      setToken(getStoredToken());
    }
    window.addEventListener(AUTH_CHANGED_EVENT, syncAuthState);
    window.addEventListener("storage", syncAuthState);
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, syncAuthState);
      window.removeEventListener("storage", syncAuthState);
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      async login(username: string, password: string) {
        const payload = await loginRequest(username, password);
        setUser(payload.user);
        setToken(payload.access_token);
      },
      async logout() {
        await logoutRequest();
        clearAuth();
        setUser(null);
        setToken(null);
      },
      hasPermission(permission: string) {
        return Boolean(user?.permissions.includes(permission));
      }
    }),
    [user, token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
