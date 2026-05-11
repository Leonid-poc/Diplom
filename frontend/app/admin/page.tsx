"use client";
import dynamic from "next/dynamic";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { api, type BusStop } from "@/lib/api";

const LeafletMap = dynamic(() => import("@/components/map/LeafletMap"), {
  ssr: false,
  loading: () => <div className="h-[500px] bg-muted animate-pulse rounded-md" />,
});

export default function AdminPage() {
  const stopsQ = useQuery({ queryKey: ["bus_stops"], queryFn: () => api<BusStop[]>("/bus_stops") });

  return (
    <AppShell>
      <h1 className="text-2xl font-bold mb-6">НСИ — справочники</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Остановочные пункты ({stopsQ.data?.length ?? 0})</CardTitle>
          </CardHeader>
          <CardContent className="p-0 max-h-[600px] overflow-y-auto">
            {stopsQ.isLoading ? (
              <div className="p-6 text-sm text-muted-foreground">Загрузка…</div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Название</TableHead>
                    <TableHead>Координаты</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {stopsQ.data?.map((s) => (
                    <TableRow key={s.id}>
                      <TableCell>{s.id}</TableCell>
                      <TableCell>{s.name}</TableCell>
                      <TableCell className="font-mono text-xs">
                        {Number(s.lat).toFixed(5)}, {Number(s.lon).toFixed(5)}
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
          </CardHeader>
          <CardContent className="h-[600px] p-0">
            <LeafletMap stops={stopsQ.data ?? []} className="h-full w-full rounded-b-md overflow-hidden" />
          </CardContent>
        </Card>
      </div>
    </AppShell>
  );
}
