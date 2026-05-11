"use client";
import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Save, MapPin, ChevronDown, ChevronUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { api, ApiError, type BusStop, type BuildRouteResponse } from "@/lib/api";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[500px] bg-muted animate-pulse rounded-md" />,
});

type Algorithm = "osrm" | "dijkstra" | "astar";

export function RouteBuilder() {
  const qc = useQueryClient();
  const stopsQ = useQuery({ queryKey: ["bus_stops"], queryFn: () => api<BusStop[]>("/bus_stops") });

  const [start, setStart] = useState<number | null>(null);
  const [end, setEnd] = useState<number | null>(null);
  const [algo, setAlgo] = useState<Algorithm>("osrm");
  const [snapRadius, setSnapRadius] = useState(80);  // метры
  const [minSpacing, setMinSpacing] = useState(200); // метры
  const [result, setResult] = useState<BuildRouteResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ---- Build mutation ----
  const buildMutation = useMutation({
    mutationFn: () =>
      api<BuildRouteResponse>("/routes/build", {
        method: "POST",
        body: {
          start_stop_id: start,
          end_stop_id: end,
          algorithm: algo,
          snap_radius_m: snapRadius,
          min_stop_spacing_m: minSpacing,
        },
      }),
    onSuccess: (data) => {
      setResult(data);
      setError(null);
    },
    onError: (err) => setError(err instanceof ApiError ? err.detail : "Ошибка"),
  });

  // ---- Save mutation ----
  const [saveOpen, setSaveOpen] = useState(false);
  const [routeNumber, setRouteNumber] = useState("");
  const [routeName, setRouteName] = useState("");
  const [routeType, setRouteType] = useState("городской");
  const [savedOk, setSavedOk] = useState(false);
  const [stopsExpanded, setStopsExpanded] = useState(true);

  const saveMutation = useMutation({
    mutationFn: () =>
      api("/routes", {
        method: "POST",
        body: {
          route_number: routeNumber,
          name: routeName,
          type: routeType,
          total_length: result?.total_distance_km,
          estimated_time_min: result?.estimated_time_min,
          algorithm: result?.algorithm,
          geometry: result?.geometry ?? [],
          stop_ids: result?.path ?? [],
        },
      }),
    onSuccess: () => {
      setSavedOk(true);
      qc.invalidateQueries({ queryKey: ["routes"] });
      setTimeout(() => {
        setSaveOpen(false);
        setSavedOk(false);
        setRouteNumber("");
        setRouteName("");
      }, 800);
    },
  });

  const stopById = useMemo(() => {
    const m = new Map<number, BusStop>();
    stopsQ.data?.forEach((s) => m.set(s.id, s));
    return m;
  }, [stopsQ.data]);

  // Подсвеченные остановки (для карты) — берём из matched_stops
  const highlightedStops = useMemo(
    () =>
      (result?.matched_stops ?? []).map((m) => ({
        id: m.id,
        name: m.name,
        lat: m.lat,
        lon: m.lon,
      })),
    [result],
  );

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
                onChange={(e) => setAlgo(e.target.value as Algorithm)}
              >
                <option value="osrm">OSRM (по реальным дорогам)</option>
                <option value="dijkstra">Дейкстра (граф остановок)</option>
                <option value="astar">A* (граф остановок)</option>
              </select>
            </div>

            {algo === "osrm" && (
              <>
                <div className="space-y-1">
                  <Label>Радиус подбора остановок: {snapRadius} м</Label>
                  <input
                    type="range"
                    min={20}
                    max={300}
                    step={10}
                    value={snapRadius}
                    onChange={(e) => setSnapRadius(Number(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">
                    Какое отклонение остановки от линии маршрута считать «по пути»
                  </p>
                </div>
                <div className="space-y-1">
                  <Label>Мин. интервал между остановками: {minSpacing} м</Label>
                  <input
                    type="range"
                    min={50}
                    max={1000}
                    step={50}
                    value={minSpacing}
                    onChange={(e) => setMinSpacing(Number(e.target.value))}
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">
                    Для прореживания «двойников» — обе стороны улицы
                  </p>
                </div>
              </>
            )}

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
            <CardHeader className="flex flex-row items-start justify-between">
              <CardTitle>Результат</CardTitle>
              <Badge variant={result.source === "osrm" ? "default" : "secondary"}>
                {result.source === "osrm" ? "реальные дороги" : "граф"}
              </Badge>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex justify-between"><span>Протяжённость:</span><span className="font-mono">{result.total_distance_km} км</span></div>
              <div className="flex justify-between"><span>Время следования:</span><span className="font-mono">{result.estimated_time_min} мин</span></div>
              <div className="flex justify-between"><span>Требуется ТС:</span><span className="font-mono">{result.required_vehicles}</span></div>
              <div className="flex justify-between"><span>Интервал:</span><span className="font-mono">{result.interval_min} мин</span></div>
              <div className="flex justify-between"><span>Алгоритм:</span><span className="font-mono">{result.algorithm}</span></div>

              {/* ----- Остановки по маршруту (выпадающий список) ----- */}
              {(() => {
                const stopsCount = result.matched_stops?.length ?? result.path?.length ?? 0;
                const stops =
                  result.matched_stops && result.matched_stops.length
                    ? result.matched_stops
                    : (result.path ?? []).map((id) => {
                        const s = stopById.get(id);
                        return s
                          ? {
                              id: s.id,
                              name: s.name,
                              lat: Number(s.lat),
                              lon: Number(s.lon),
                              distance_from_route_m: 0,
                            }
                          : null;
                      }).filter(Boolean) as { id: number; name: string; lat: number; lon: number; distance_from_route_m: number }[];

                const isOk = stopsCount >= 2;
                return (
                  <div className="border-t pt-2 mt-2">
                    <button
                      type="button"
                      onClick={() => setStopsExpanded((v) => !v)}
                      className="flex w-full items-center justify-between hover:bg-muted/50 rounded px-1 py-1"
                    >
                      <span className="font-medium">
                        Остановок по пути:{" "}
                        <span className={isOk ? "text-primary" : "text-destructive"}>
                          {stopsCount}
                        </span>
                        {result.source === "osrm" && stopsCount <= 2 && (
                          <span className="ml-2 text-xs text-amber-600">
                            (только начало/конец — увеличьте радиус)
                          </span>
                        )}
                      </span>
                      {stopsExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </button>

                    {stopsExpanded && stops.length > 0 && (
                      <div className="mt-2 max-h-[300px] overflow-y-auto border rounded bg-muted/20">
                        {stops.map((s, idx) => (
                          <div
                            key={s.id}
                            className="flex items-start gap-2 px-2 py-1.5 border-b last:border-b-0 hover:bg-background"
                          >
                            <MapPin size={12} className="mt-1 shrink-0 text-primary" />
                            <div className="flex-1 min-w-0">
                              <div className="text-xs font-medium truncate">
                                {idx + 1}. {s.name}
                              </div>
                              {result.source === "osrm" && (
                                <div className="text-[10px] text-muted-foreground">
                                  отклонение: {s.distance_from_route_m.toFixed(0)} м
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })()}

              <Dialog open={saveOpen} onOpenChange={setSaveOpen}>
                <DialogTrigger asChild>
                  <Button className="w-full mt-3">
                    <Save size={16} className="mr-2" />
                    Сохранить маршрут
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Сохранение маршрута</DialogTitle>
                  </DialogHeader>
                  <div className="space-y-3 py-2">
                    <div className="space-y-1">
                      <Label>Номер маршрута</Label>
                      <Input
                        placeholder="например, 11"
                        value={routeNumber}
                        onChange={(e) => setRouteNumber(e.target.value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>Название</Label>
                      <Input
                        placeholder={`${stopById.get(start ?? 0)?.name ?? ""} — ${stopById.get(end ?? 0)?.name ?? ""}`}
                        value={routeName}
                        onChange={(e) => setRouteName(e.target.value)}
                      />
                    </div>
                    <div className="space-y-1">
                      <Label>Тип</Label>
                      <select
                        className="w-full border rounded-md h-10 px-3 text-sm bg-background"
                        value={routeType}
                        onChange={(e) => setRouteType(e.target.value)}
                      >
                        <option value="городской">городской</option>
                        <option value="пригородный">пригородный</option>
                        <option value="экспресс">экспресс</option>
                      </select>
                    </div>
                    {saveMutation.isError && (
                      <p className="text-sm text-destructive">
                        {saveMutation.error instanceof ApiError
                          ? saveMutation.error.detail
                          : "Ошибка сохранения"}
                      </p>
                    )}
                    {savedOk && <p className="text-sm text-emerald-600">Сохранено!</p>}
                  </div>
                  <DialogFooter>
                    <Button
                      disabled={!routeNumber || !routeName || saveMutation.isPending}
                      onClick={() => saveMutation.mutate()}
                    >
                      {saveMutation.isPending ? "Сохранение…" : "Сохранить"}
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </CardContent>
          </Card>
        )}

      </div>

      <div className="lg:col-span-2">
        <Card>
          <CardHeader>
            <CardTitle>Карта</CardTitle>
          </CardHeader>
          <CardContent className="h-[700px] p-0">
            <LeafletMap
              stops={stopsQ.data ?? []}
              routeGeometry={result?.geometry as [number, number][] | undefined}
              highlightedStops={highlightedStops}
              className="h-full w-full rounded-b-md overflow-hidden"
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
