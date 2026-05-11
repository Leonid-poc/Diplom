"use client";
import { create } from "zustand";

type AuthState = {
  token: string | null;
  user: { id: number; login: string; full_name: string; role: string } | null;
  setToken: (t: string | null) => void;
  setUser: (u: AuthState["user"]) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  token: typeof window !== "undefined" ? localStorage.getItem("auth_token") : null,
  user: null,
  setToken: (t) => {
    if (typeof window !== "undefined") {
      if (t) localStorage.setItem("auth_token", t);
      else localStorage.removeItem("auth_token");
    }
    set({ token: t });
  },
  setUser: (u) => set({ user: u }),
  logout: () => {
    if (typeof window !== "undefined") localStorage.removeItem("auth_token");
    set({ token: null, user: null });
  },
}));
