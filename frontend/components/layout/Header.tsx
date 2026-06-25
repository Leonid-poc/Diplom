"use client";
import { useRouter } from "next/navigation";
import { Menu, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/stores/auth-store";

type Props = {
  onMenuClick: () => void;
};

export function Header({ onMenuClick }: Props) {
  const router = useRouter();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b px-3 sm:px-6">
      <div className="flex items-center gap-2 min-w-0">
        <button
          onClick={onMenuClick}
          className="rounded-sm p-1 hover:bg-accent lg:hidden shrink-0"
          aria-label="Открыть меню"
        >
          <Menu size={20} />
        </button>
        <span className="text-xs sm:text-sm text-muted-foreground truncate">
          Л.Е. Георг · ОГУ · 22ПИнж(б)РПИС-1
        </span>
      </div>
      <div className="flex items-center gap-2 sm:gap-4 shrink-0">
        {user && (
          <div className="hidden sm:block text-sm">
            <span className="font-medium">{user.full_name}</span>
            <span className="ml-2 text-muted-foreground">({user.role})</span>
          </div>
        )}
        <Button variant="ghost" size="sm" onClick={handleLogout}>
          <LogOut size={16} className="sm:mr-1" />
          <span className="hidden sm:inline">Выйти</span>
        </Button>
      </div>
    </header>
  );
}
