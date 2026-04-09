"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { API_BASE } from "@/lib/api";

interface User {
  id: number;
  username: string;
  role: string;
  email: string | null;
  is_active: boolean;
  avatar_url?: string | null;
  display_name?: string | null;
  bio?: string | null;
  created_at?: string | null;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  updateAvatarUrl: (url: string | null) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem("ukip_token");
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(getStoredToken);
  const [user, setUser]   = useState<User | null>(null);

  useEffect(() => {
    if (!token) {
      return;
    }

    let cancelled = false;
    fetch(`${API_BASE}/users/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (!cancelled && data) {
          setUser(data);
        }
      })
      .catch(() => {});

    return () => {
      cancelled = true;
    };
  }, [token]);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) setUser(await res.json());
    } catch { /* non-critical */ }
  }, [token]);

  const updateAvatarUrl = useCallback((url: string | null) => {
    setUser(prev => prev ? { ...prev, avatar_url: url } : prev);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const body = new URLSearchParams({ username, password });
    const res = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: body.toString(),
    });
    if (!res.ok) {
      throw new Error("Invalid credentials");
    }
    const data = await res.json();
    localStorage.setItem("ukip_token", data.access_token);
    setToken(data.access_token);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("ukip_token");
    setToken(null);
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ token, user, isAuthenticated: !!token, login, logout, refreshUser, updateAvatarUrl }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
}
