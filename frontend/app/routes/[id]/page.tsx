"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import { MapPin } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { api, type RouteDetail } from "@/lib/api";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[400px] bg-muted animate-pulse rounded-md" />,
});

export default function RouteDetailsPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data, isLoading, error } = useQuery({
    queryKey: ["route", id],
    queryFn: () => api<RouteDetail>(`/routes/${id}`),
    enabled: !Number.isNaN(id),
  });

  if (isLoading) {
    return (
      <AppShell>
        <p className="text-muted-foreground">Загрузка…</p>
      </AppShell>
    );
  }

  if (error || !data) {
    return (
      <AppShell>
        <p className="text-destructive">Маршрут не найден</p>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">
        №{data.route_number} — {data.name}
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Карточка метрик */}
        <Card>
          <CardHeader>
            <CardTitle>Параметры</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Тип</span>
              <span>{data.type}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Статус</span>
              {data.is_active ? <Badge>активный</Badge> : <Badge variant="secondary">неактивный</Badge>}
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Длина</span>
              <span className="font-mono">{String(data.total_length)} км</span>
            </div>
            {data.estimated_time_min != null && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Время следования</span>
                <span className="font-mono">{data.estimated_time_min} мин</span>
              </div>
            )}
            {data.algorithm && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Алгоритм</span>
                <span className="font-mono">{data.algorithm}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-muted-foreground">Остановок</span>
              <span className="font-mono">{data.stops.length}</span>
            </div>
            <div className="pt-2 text-xs text-muted-foreground border-t">
              Создан: {new Date(data.created_at).toLocaleString("ru-RU")}
              <br />
              Обновлён: {new Date(data.updated_at).toLocaleString("ru-RU")}
            </div>
            {data.description && (
              <div className="pt-2 border-t text-xs text-muted-foreground">{data.description}</div>
            )}
          </CardContent>
        </Card>

        {/* Карта */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Геометрия маршрута</CardTitle>
          </CardHeader>
          <CardContent className="h-[400px] p-0">
            <LeafletMap
              routeGeometry={data.geometry as [number, number][]}
              highlightedStops={data.stops.map((s) => ({
                id: s.stop_id,
                name: s.name,
                lat: s.lat,
                lon: s.lon,
              }))}
              className="h-full w-full rounded-b-md overflow-hidden"
            />
          </CardContent>
        </Card>
      </div>

      {/* Список остановок */}
      <Card>
        <CardHeader>
          <CardTitle>Остановки по маршруту ({data.stops.length})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">№</TableHead>
                <TableHead>Название</TableHead>
                <TableHead className="w-28">Широта</TableHead>
                <TableHead className="w-28">Долгота</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.stops.map((s) => (
                <TableRow key={`${s.stop_id}-${s.order_num}`}>
                  <TableCell className="font-mono text-xs">{s.order_num}</TableCell>
                  <TableCell>
                    <span className="flex items-center gap-1">
                      <MapPin size={12} className="text-primary shrink-0" />
                      {s.name}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-xs">{s.lat.toFixed(5)}</TableCell>
                  <TableCell className="font-mono text-xs">{s.lon.toFixed(5)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </AppShell>
  );
}
