"use client";
import { AppShell } from "@/components/layout/AppShell";
import { RouteBuilder } from "@/components/routes/RouteBuilder";

export default function NewRoutePage() {
  return (
    <AppShell>
      <h1 className="text-xl sm:text-2xl font-bold mb-4 sm:mb-6">Расчёт нового маршрута</h1>
      <RouteBuilder />
    </AppShell>
  );
}
