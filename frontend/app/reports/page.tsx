"use client";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/AppShell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell } from "@/components/ui/table";
import { api } from "@/lib/api";

type Report = {
  id: number;
  title: string;
  author_id: number | null;
  created_at: string;
};

export default function ReportsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: () => api<Report[]>("/reports"),
  });

  return (
    <AppShell>
      <h1 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Аналитические отчёты</h1>
      <Card>
        <CardHeader>
          <CardTitle>Сохранённые отчёты</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 text-sm text-muted-foreground">Загрузка…</div>
          ) : !data?.length ? (
            <div className="p-6 text-sm text-muted-foreground">
              Отчётов пока нет. Запустите кластерный анализ и сохраните результат.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Название</TableHead>
                  <TableHead className="hidden sm:table-cell">Дата</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell>{r.id}</TableCell>
                    <TableCell>{r.title}</TableCell>
                    <TableCell className="hidden sm:table-cell">{new Date(r.created_at).toLocaleString("ru-RU")}</TableCell>
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
