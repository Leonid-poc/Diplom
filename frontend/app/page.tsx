"use client";
import { useQuery } from "@tanstack/react-query";
import { Map, Bus, Activity, TrendingUp } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { KpiCard } from "@/components/kpi/KpiCard";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { api, type Route, type BusStop } from "@/lib/api";

export default function Dashboard() {
  const routesQ = useQuery({ queryKey: ["routes"], queryFn: () => api<Route[]>("/routes") });
  const stopsQ = useQuery({ queryKey: ["bus_stops"], queryFn: () => api<BusStop[]>("/bus_stops") });

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Главная</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <KpiCard
          title="Маршрутов"
          value={routesQ.data?.length ?? "—"}
          Icon={Map}
          hint="Активная маршрутная сеть"
        />
        <KpiCard
          title="Остановочных пунктов"
          value={stopsQ.data?.length ?? "—"}
          Icon={Bus}
          hint="Всего в реестре"
        />
        <KpiCard
          title="Активных рейсов"
          value="—"
          Icon={Activity}
          hint="Данные из ВИС"
        />
        <KpiCard
          title="Эффективность сети"
          value="—"
          Icon={TrendingUp}
          hint="Интегральный индекс"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>О системе</CardTitle>
        </CardHeader>
        <CardContent className="text-sm leading-relaxed space-y-2">
          <p>
            ПИС «Маршрут» — программно-информационная система автоматизированного
            проектирования городских маршрутов пассажирских перевозок.
          </p>
          <p>
            Реализация: FastAPI · Next.js · PostgreSQL · Leaflet/OpenStreetMap.
            Соответствует ВКР Л.Е. Георга (ОГУ, 09.03.04, шифр ОГУ 09.03.04.3025.755 ПЗ).
          </p>
        </CardContent>
      </Card>
    </AppShell>
  );
}
