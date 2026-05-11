"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/lib/api";

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, user, setUser, logout } = useAuthStore();

  useEffect(() => {
    if (!token) {
      router.push("/login");
      return;
    }
    if (!user) {
      api<typeof user>("/auth/me")
        .then((u) => setUser(u as any))
        .catch(() => {
          logout();
          router.push("/login");
        });
    }
  }, [token, user, router, setUser, logout]);

  if (!token) return null;

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
