"use client";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { api, type Route } from "@/lib/api";

export default function RoutesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["routes"],
    queryFn: () => api<Route[]>("/routes"),
  });

  return (
    <AppShell>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Маршруты</h1>
        <Link href="/routes/new">
          <Button>
            <Plus size={16} className="mr-1" />
            Рассчитать новый
          </Button>
        </Link>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 text-sm text-muted-foreground">Загрузка…</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>№</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead>Тип</TableHead>
                  <TableHead>Длина, км</TableHead>
                  <TableHead>Статус</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.route_number}</TableCell>
                    <TableCell>
                      <Link href={`/routes/${r.id}`} className="hover:underline">
                        {r.name}
                      </Link>
                    </TableCell>
                    <TableCell>{r.type}</TableCell>
                    <TableCell>{String(r.total_length)}</TableCell>
                    <TableCell>
                      {r.is_active ? <Badge>активный</Badge> : <Badge variant="secondary">неактивный</Badge>}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
