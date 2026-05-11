"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { api, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth-store";

export default function LoginPage() {
  const router = useRouter();
  const setToken = useAuthStore((s) => s.setToken);
  const [login, setLogin] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const r = await api<{ access_token: string }>("/auth/login", {
        method: "POST",
        body: { login, password },
        auth: false,
      });
      setToken(r.access_token);
      router.push("/");
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Ошибка авторизации");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-muted/30 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Авторизация</CardTitle>
          <CardDescription>
            ПИС «Маршрут» — проектирование городских маршрутов пассажирских перевозок
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="login">Логин</Label>
              <Input id="login" value={login} onChange={(e) => setLogin(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Вход…" : "Войти"}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              Тестовые учётные записи:&nbsp;
              <code>admin/admin123</code>,&nbsp;
              <code>analyst/analyst123</code>,&nbsp;
              <code>manager/manager123</code>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
