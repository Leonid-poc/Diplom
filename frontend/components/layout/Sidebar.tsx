"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Map,
  Bus,
  BarChart3,
  FileText,
  Settings,
} from "lucide-react";

const NAV = [
  { href: "/",          label: "Главная",        icon: LayoutDashboard },
  { href: "/routes",    label: "Маршруты",       icon: Map },
  { href: "/admin",     label: "НСИ (справочники)", icon: Bus },
  { href: "/analytics", label: "Анализ",         icon: BarChart3 },
  { href: "/reports",   label: "Отчёты",         icon: FileText },
];

export function Sidebar() {
  const path = usePathname();
  return (
    <aside className="w-64 shrink-0 border-r bg-muted/30 p-4 space-y-1">
      <div className="px-2 pb-4 mb-2 border-b">
        <div className="text-sm font-semibold">ПИС «Маршрут»</div>
        <div className="text-xs text-muted-foreground">ОГУ 09.03.04.3025.755 ПЗ</div>
      </div>
      {NAV.map((item) => {
        const Icon = item.icon;
        const active = path === item.href || (item.href !== "/" && path.startsWith(item.href));
        return (
          <Link
            key={item.href}
            href={item.href}
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
    </aside>
  );
}
