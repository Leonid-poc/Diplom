// Тонкий обёрточный клиент к FastAPI с автоматическим Bearer-токеном.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

type RequestOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  auth?: boolean;
};

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("auth_token");
}

export class ApiError extends Error {
  constructor(public status: number, public detail: string) {
    super(detail);
  }
}

export async function api<T = unknown>(
  path: string,
  opts: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (opts.auth !== false) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, {
    method: opts.method ?? "GET",
    headers,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    cache: "no-store",
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// Типы (повторяют pydantic-схемы FastAPI)
export type BusStop = {
  id: number;
  name: string;
  lat: string | number;
  lon: string | number;
  address?: string | null;
  has_pavilion: boolean;
};

export type Route = {
  id: number;
  route_number: string;
  name: string;
  type: string;
  total_length: string | number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type RouteStopDetail = {
  stop_id: number;
  name: string;
  lat: number;
  lon: number;
  order_num: number;
};

export type RouteDetail = Route & {
  geometry: [number, number][];
  estimated_time_min: number | null;
  algorithm: string | null;
  stops: RouteStopDetail[];
};

export type MatchedStop = {
  id: number;
  name: string;
  lat: number;
  lon: number;
  distance_from_route_m: number;
};

export type BuildRouteResponse = {
  path: number[];
  matched_stops: MatchedStop[];
  geometry: [number, number][];  // [[lat, lon], ...]
  total_distance_km: number;
  estimated_time_min: number;
  required_vehicles: number;
  interval_min: number;
  algorithm: string;
  source: "osrm" | "graph";
};

export type ClusterPoint = {
  route_id: number;
  route_number: string;
  cluster: number;
  efficiency: number;
  features: number[];
};

export type ClusterResponse = {
  points: ClusterPoint[];
  centers: number[][];
  n_clusters: number;
  method: string;
};
