"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import {
  LayoutDashboard,
  Map,
  Bus,
  BarChart3,
  FileText,
} from "lucide-react";

const NAV = [
  { href: "/",          label: "Главная",        icon: LayoutDashboard },
  { href: "/routes",    label: "Маршруты",       icon: Map },
  { href: "/admin",     label: "НСИ (справочники)", icon: Bus },
  { href: "/analytics", label: "Анализ",         icon: BarChart3 },
  { href: "/reports",   label: "Отчёты",         icon: FileText },
];

type Props = {
  open: boolean;
  onNavigate: () => void;
};

export function Sidebar({ open, onNavigate }: Props) {
  const path = usePathname();
  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r bg-muted/30 p-4 transition-transform duration-200",
        "lg:relative lg:z-auto lg:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full",
      )}
    >
      {/* Close button (mobile only) */}
      <button
        onClick={onNavigate}
        className="absolute right-3 top-3 rounded-sm p-1 hover:bg-accent lg:hidden"
        aria-label="Закрыть меню"
      >
        <X size={18} />
      </button>

      <div className="px-2 pb-4 mb-2 border-b">
        <div className="text-sm font-semibold">ПИС «Маршрут»</div>
        <div className="text-xs text-muted-foreground">ОГУ 09.03.04.3025.755 ПЗ</div>
      </div>
      <nav className="space-y-1">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active = path === item.href || (item.href !== "/" && path.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-accent hover:text-accent-foreground",
              )}
            >
              <Icon size={16} />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
