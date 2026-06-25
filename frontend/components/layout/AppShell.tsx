"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Header } from "./Header";
import { useAuthStore } from "@/stores/auth-store";
import { api } from "@/lib/api";

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { token, user, setUser, logout } = useAuthStore();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const closeSidebar = useCallback(() => setSidebarOpen(false), []);

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

  // Close sidebar on any navigation (mobile UX)
  useEffect(() => {
    closeSidebar();
  }, [children, closeSidebar]);

  if (!token) return null;

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile-only backdrop overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={closeSidebar}
        />
      )}
      <Sidebar open={sidebarOpen} onNavigate={closeSidebar} />
      <div className="flex flex-1 flex-col overflow-hidden min-w-0">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 overflow-y-auto p-3 sm:p-4 md:p-6">{children}</main>
      </div>
    </div>
  );
}
