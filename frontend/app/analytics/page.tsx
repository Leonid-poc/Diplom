"use client";
import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { api, ApiError, type ClusterResponse } from "@/lib/api";

const CLUSTER_COLORS = ["bg-blue-500", "bg-emerald-500", "bg-amber-500", "bg-rose-500", "bg-violet-500"];

export default function AnalyticsPage() {
  const [periodDays, setPeriodDays] = useState(30);
  const [nClusters, setNClusters] = useState(4);
  const [result, setResult] = useState<ClusterResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mut = useMutation({
    mutationFn: () =>
      api<ClusterResponse>("/analytics/cluster", {
        method: "POST",
        body: { period_days: periodDays, n_clusters: nClusters },
      }),
    onSuccess: (data) => {
      setResult(data);
      setError(null);
    },
    onError: (err) => setError(err instanceof ApiError ? err.detail : "Ошибка"),
  });

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">Кластерный анализ маршрутов</h1>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Параметры анализа</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap items-end gap-4">
          <div className="space-y-1">
            <Label>Период (дней)</Label>
            <Input
              type="number"
              min={1}
              max={365}
              value={periodDays}
              onChange={(e) => setPeriodDays(Number(e.target.value))}
              className="w-32"
            />
          </div>
          <div className="space-y-1">
            <Label>Число кластеров (k)</Label>
            <Input
              type="number"
              min={2}
              max={10}
              value={nClusters}
              onChange={(e) => setNClusters(Number(e.target.value))}
              className="w-32"
            />
          </div>
          <Button disabled={mut.isPending} onClick={() => mut.mutate()}>
            {mut.isPending ? "Анализ…" : "Запустить анализ"}
          </Button>
          {error && <p className="text-sm text-destructive ml-4">{error}</p>}
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Результаты ({result.method}, k = {result.n_clusters})</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>№ маршрута</TableHead>
                  <TableHead>Кластер</TableHead>
                  <TableHead>Длина, км</TableHead>
                  <TableHead>Время, мин</TableHead>
                  <TableHead>Загрузка</TableHead>
                  <TableHead>Эффективность</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {result.points
                  .slice()
                  .sort((a, b) => b.efficiency - a.efficiency)
                  .map((p) => (
                    <TableRow key={p.route_id}>
                      <TableCell className="font-medium">{p.route_number}</TableCell>
                      <TableCell>
                        <span
                          className={`inline-block w-3 h-3 rounded-full mr-2 ${
                            CLUSTER_COLORS[p.cluster % CLUSTER_COLORS.length]
                          }`}
                        />
                        Кластер {p.cluster + 1}
                      </TableCell>
                      <TableCell>{p.features[0]?.toFixed(2)}</TableCell>
                      <TableCell>{p.features[1]?.toFixed(1)}</TableCell>
                      <TableCell>{p.features[2]?.toFixed(0)}</TableCell>
                      <TableCell>
                        <Badge variant={p.efficiency > 0.5 ? "default" : "secondary"}>
                          {p.efficiency.toFixed(3)}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </AppShell>
  );
}
