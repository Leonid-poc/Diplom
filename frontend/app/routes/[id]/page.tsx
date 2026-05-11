"use client";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { api, type Route } from "@/lib/api";

export default function RouteDetailsPage() {
  const params = useParams();
  const id = Number(params.id);
  const { data, isLoading } = useQuery({
    queryKey: ["route", id],
    queryFn: () => api<Route>(`/routes/${id}`),
    enabled: !Number.isNaN(id),
  });

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Маршрут</h1>
      {isLoading ? (
        <p className="text-muted-foreground">Загрузка…</p>
      ) : data ? (
        <Card>
          <CardHeader>
            <CardTitle>
              №{data.route_number} — {data.name}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div>Тип: {data.type}</div>
            <div>Длина: {String(data.total_length)} км</div>
            <div>Статус: {data.is_active ? <Badge>активный</Badge> : <Badge variant="secondary">неактивный</Badge>}</div>
            <div className="pt-2 text-xs text-muted-foreground">
              Создан: {new Date(data.created_at).toLocaleString("ru-RU")}<br />
              Обновлён: {new Date(data.updated_at).toLocaleString("ru-RU")}
            </div>
          </CardContent>
        </Card>
      ) : (
        <p>Не найдено</p>
      )}
    </AppShell>
  );
}
