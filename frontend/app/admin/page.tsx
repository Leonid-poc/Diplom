"use client";
import { useState } from "react";
import dynamic from "next/dynamic";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2 } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { api, ApiError, type BusStop } from "@/lib/api";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[350px] sm:h-[500px] lg:h-[600px] bg-muted animate-pulse rounded-md" />,
});

export default function AdminPage() {
  const qc = useQueryClient();
  const stopsQ = useQuery({
    queryKey: ["bus_stops"],
    queryFn: () => api<BusStop[]>("/bus_stops"),
  });

  // ---- Add stop form ----
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [address, setAddress] = useState("");
  const [hasPavilion, setHasPavilion] = useState(false);

  const resetForm = () => {
    setName("");
    setLat("");
    setLon("");
    setAddress("");
    setHasPavilion(false);
  };

  const addMutation = useMutation({
    mutationFn: () =>
      api("/bus_stops", {
        method: "POST",
        body: {
          name,
          lat: parseFloat(lat),
          lon: parseFloat(lon),
          address: address || null,
          has_pavilion: hasPavilion,
        },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["bus_stops"] });
      setOpen(false);
      resetForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api(`/bus_stops/${id}`, { method: "DELETE" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bus_stops"] }),
  });

  const handleMapClick = (clickedLat: number, clickedLon: number) => {
    setLat(clickedLat.toFixed(7));
    setLon(clickedLon.toFixed(7));
    setOpen(true);
  };

  return (
    <AppShell>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4 sm:mb-6">
        <h1 className="text-xl sm:text-2xl font-bold">НСИ — справочники</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <Button onClick={() => setOpen(true)} className="w-full sm:w-auto">
            <Plus size={16} className="mr-1" />
            Добавить остановку
          </Button>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Новая остановка</DialogTitle>
            </DialogHeader>
            <div className="space-y-3 py-2">
              <div className="space-y-1">
                <Label>Название *</Label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="например, пр. Победы" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <Label>Широта *</Label>
                  <Input
                    type="number"
                    step="0.0000001"
                    value={lat}
                    onChange={(e) => setLat(e.target.value)}
                    placeholder="51.7682"
                  />
                </div>
                <div className="space-y-1">
                  <Label>Долгота *</Label>
                  <Input
                    type="number"
                    step="0.0000001"
                    value={lon}
                    onChange={(e) => setLon(e.target.value)}
                    placeholder="55.0972"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label>Адрес</Label>
                <Input value={address} onChange={(e) => setAddress(e.target.value)} placeholder="(необязательно)" />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={hasPavilion}
                  onChange={(e) => setHasPavilion(e.target.checked)}
                />
                Есть павильон
              </label>
              <p className="text-xs text-muted-foreground">
                Подсказка: можно кликнуть по нужной точке на карте — координаты подставятся автоматически.
              </p>
              {addMutation.isError && (
                <p className="text-sm text-destructive">
                  {addMutation.error instanceof ApiError ? addMutation.error.detail : "Ошибка"}
                </p>
              )}
            </div>
            <DialogFooter>
              <Button
                disabled={!name || !lat || !lon || addMutation.isPending}
                onClick={() => addMutation.mutate()}
              >
                {addMutation.isPending ? "Сохранение…" : "Сохранить"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Остановочные пункты ({stopsQ.data?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent className="p-0 max-h-[60vh] lg:max-h-[600px] overflow-y-auto">
            {stopsQ.isLoading ? (
              <div className="p-6 text-sm text-muted-foreground">Загрузка…</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Название</TableHead>
                    <TableHead className="hidden sm:table-cell">Координаты</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stopsQ.data?.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>{s.id}</TableCell>
                      <TableCell>{s.name}</TableCell>
                      <TableCell className="hidden sm:table-cell font-mono text-xs">
                        {Number(s.lat).toFixed(5)}, {Number(s.lon).toFixed(5)}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => {
                            if (confirm(`Удалить остановку «${s.name}»?`)) {
                              deleteMutation.mutate(s.id);
                            }
                          }}
                        >
                          <Trash2 size={14} className="text-destructive" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Карта остановок</CardTitle>
            <p className="text-xs text-muted-foreground">
              Кликните по карте, чтобы добавить остановку в этой точке
            </p>
          </CardHeader>
          <CardContent className="h-[350px] sm:h-[500px] lg:h-[600px] p-0">
            <LeafletMap
              stops={stopsQ.data ?? []}
              onMapClick={handleMapClick}
              className="h-full w-full rounded-b-md overflow-hidden"
            />
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
