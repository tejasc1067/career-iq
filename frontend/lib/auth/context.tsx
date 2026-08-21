"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  clearAccessToken,
  login as requestLogin,
  logout as requestLogout,
  refreshSession,
  type LoginOutcome,
} from "@/lib/auth/session";

export type AuthStatus = "loading" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  status: AuthStatus;
  signIn: (email: string, password: string) => Promise<LoginOutcome>;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const restored = useRef(false);

  useEffect(() => {
    if (restored.current) {
      return;
    }
    restored.current = true;

    let active = true;
    refreshSession().then((token) => {
      if (active) {
        setStatus(token ? "authenticated" : "unauthenticated");
      }
    });
    return () => {
      active = false;
    };
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    const outcome = await requestLogin(email, password);
    setStatus(outcome.ok ? "authenticated" : "unauthenticated");
    return outcome;
  }, []);

  const signOut = useCallback(async () => {
    await requestLogout();
    clearAccessToken();
    setStatus("unauthenticated");
  }, []);

  return (
    <AuthContext.Provider value={{ status, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return value;
}
