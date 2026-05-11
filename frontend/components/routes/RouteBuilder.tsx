"use client";
import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { api, ApiError, type BusStop, type BuildRouteResponse } from "@/lib/api";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[500px] bg-muted animate-pulse rounded-md" />,
});

export function RouteBuilder() {
  const stopsQ = useQuery({ queryKey: ["bus_stops"], queryFn: () => api<BusStop[]>("/bus_stops") });
  const [start, setStart] = useState<number | null>(null);
  const [end, setEnd] = useState<number | null>(null);
  const [algo, setAlgo] = useState<"dijkstra" | "astar">("dijkstra");
  const [result, setResult] = useState<BuildRouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const buildMutation = useMutation({
    mutationFn: () =>
      api<BuildRouteResponse>("/routes/build", {
        method: "POST",
        body: { start_stop_id: start, end_stop_id: end, algorithm: algo },
      }),
    onSuccess: (data) => {
      setResult(data);
      setError(null);
    },
    onError: (err) => setError(err instanceof ApiError ? err.detail : "Ошибка"),
  });

  const stopById = useMemo(() => {
    const m = new Map<number, BusStop>();
    stopsQ.data?.forEach((s) => m.set(s.id, s));
    return m;
  }, [stopsQ.data]);

  const routeStops = result ? result.path.map((id) => stopById.get(id)).filter(Boolean) as BusStop[] : [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-1 space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Параметры расчёта</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label>Начальная остановка</Label>
              <select
                className="w-full border rounded-md h-10 px-3 text-sm bg-background"
                value={start ?? ""}
                onChange={(e) => setStart(e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">— выбрать —</option>
                {stopsQ.data?.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Конечная остановка</Label>
              <select
                className="w-full border rounded-md h-10 px-3 text-sm bg-background"
                value={end ?? ""}
                onChange={(e) => setEnd(e.target.value ? Number(e.target.value) : null)}
              >
                <option value="">— выбрать —</option>
                {stopsQ.data?.map((s) => (
                  <option key={s.id} value={s.id}>{s.name}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label>Алгоритм</Label>
              <select
                className="w-full border rounded-md h-10 px-3 text-sm bg-background"
                value={algo}
                onChange={(e) => setAlgo(e.target.value as "dijkstra" | "astar")}
              >
                <option value="dijkstra">Дейкстра</option>
                <option value="astar">A*</option>
              </select>
            </div>
            <Button
              className="w-full"
              disabled={!start || !end || buildMutation.isPending}
              onClick={() => buildMutation.mutate()}
            >
              {buildMutation.isPending ? "Расчёт…" : "Рассчитать маршрут"}
            </Button>
            {error && <p className="text-sm text-destructive">{error}</p>}
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardHeader>
              <CardTitle>Результат</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex justify-between"><span>Протяжённость:</span><span className="font-mono">{result.total_distance_km} км</span></div>
              <div className="flex justify-between"><span>Время следования:</span><span className="font-mono">{result.estimated_time_min} мин</span></div>
              <div className="flex justify-between"><span>Требуется ТС:</span><span className="font-mono">{result.required_vehicles}</span></div>
              <div className="flex justify-between"><span>Интервал:</span><span className="font-mono">{result.interval_min} мин</span></div>
              <div className="flex justify-between"><span>Алгоритм:</span><span className="font-mono">{result.algorithm}</span></div>
              <div className="pt-2 border-t mt-2 text-xs text-muted-foreground">
                Остановок в маршруте: {result.path.length}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Карта</CardTitle>
          </CardHeader>
          <CardContent className="h-[600px] p-0">
            <LeafletMap stops={stopsQ.data ?? []} routePath={routeStops} className="h-full w-full rounded-b-md overflow-hidden" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
