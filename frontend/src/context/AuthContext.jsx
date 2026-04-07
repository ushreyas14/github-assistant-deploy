import { createContext, useContext, useMemo, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("auth_token") || "");

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    const nextToken = res?.data?.user;

    if (!nextToken) {
      throw new Error("Login succeeded but token was not returned as data.user");
    }

    localStorage.setItem("auth_token", nextToken);
    setToken(nextToken);
  };

  const signup = async (email, password) => {
    await api.post("/auth/signup", { email, password });
    await login(email, password);
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (_err) {
      // Clear local auth state even if backend logout fails.
    } finally {
      localStorage.removeItem("auth_token");
      setToken("");
    }
  };

  const value = useMemo(
    () => ({ token, isAuthenticated: Boolean(token), login, signup, logout }),
    [token]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}
