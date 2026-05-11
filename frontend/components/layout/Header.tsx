"use client";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";

export function Header() {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="flex h-14 items-center justify-between border-b px-6">
      <div className="text-sm text-muted-foreground">
        Л.Е. Георг · ОГУ · 22ПИнж(б)РПИС-1
      </div>
      <div className="flex items-center gap-4">
        {user && (
          <div className="text-sm">
            <span className="font-medium">{user.full_name}</span>
            <span className="ml-2 text-muted-foreground">({user.role})</span>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          <LogOut size={16} className="mr-1" />
          Выйти
        </Button>
      </div>
    </header>
  );
}
