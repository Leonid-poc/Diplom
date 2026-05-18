"use client";
import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  CircleMarker,
  Popup,
  Polyline,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Иконки Leaflet ломаются с webpack — указываем явно
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const TILE_URL =
  process.env.NEXT_PUBLIC_MAP_TILE_URL ??
  "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const TILE_ATTR =
  process.env.NEXT_PUBLIC_MAP_ATTRIBUTION ?? "© OpenStreetMap contributors";
const CENTER_LAT = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_CENTER_LAT ?? "51.7682");
const CENTER_LON = parseFloat(process.env.NEXT_PUBLIC_DEFAULT_CENTER_LON ?? "55.0972");
const ZOOM = parseInt(process.env.NEXT_PUBLIC_DEFAULT_ZOOM ?? "12", 10);

type Stop = {
  id: number;
  name: string;
  lat: number | string;
  lon: number | string;
};

type LatLng = [number, number];

type Waypoint = {
  id: number;
  name: string;
  lat: number;
  lon: number;
  label: string;
};

type Props = {
  stops?: Stop[];
  /** Реальная геометрия маршрута (полилиния) — массив [lat, lon]. */
  routeGeometry?: LatLng[];
  /** Старый API: только список остановок маршрута — нарисуем по ним. */
  routePath?: Stop[];
  /** Подсвеченные остановки (например, подобранные вдоль маршрута). */
  highlightedStops?: Stop[];
  /** Промежуточные точки с буквенными метками. */
  waypoints?: Waypoint[];
  /** Колбэк при клике на пустое место карты — для добавления остановки. */
  onMapClick?: (lat: number, lon: number) => void;
  className?: string;
};

// Внутренний компонент-хук — слушает клики на карте
function MapClickHandler({ onClick }: { onClick?: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onClick?.(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export default function LeafletMap({
  stops,
  routeGeometry,
  routePath,
  highlightedStops,
  waypoints,
  onMapClick,
  className,
}: Props) {
  const highlightedIds = new Set(highlightedStops?.map((s) => s.id) ?? []);
  useEffect(() => {
    return () => {
      /* cleanup if needed */
    };
  }, []);

  // Определяем точки полилинии
  const polylinePoints: LatLng[] =
    routeGeometry && routeGeometry.length > 1
      ? routeGeometry
      : routePath && routePath.length > 1
        ? routePath.map((s) => [Number(s.lat), Number(s.lon)] as LatLng)
        : [];

  return (
    <div className={className ?? "h-[600px] w-full rounded-md overflow-hidden border"}>
      <MapContainer center={[CENTER_LAT, CENTER_LON]} zoom={ZOOM} scrollWheelZoom>
        <TileLayer url={TILE_URL} attribution={TILE_ATTR} />

        {onMapClick && <MapClickHandler onClick={onMapClick} />}

        {/* Все остановки — мелкими серыми точками (фон) */}
        {stops?.map((s) =>
          highlightedIds.has(s.id) ? null : (
            <CircleMarker
              key={s.id}
              center={[Number(s.lat), Number(s.lon)]}
              radius={4}
              pathOptions={{ color: "#888", fillColor: "#bbb", fillOpacity: 0.5, weight: 1 }}
            >
              <Popup>
                <strong>{s.name}</strong>
                <br />
                {Number(s.lat).toFixed(5)}, {Number(s.lon).toFixed(5)}
              </Popup>
            </CircleMarker>
          ),
        )}

        {polylinePoints.length > 1 && (
          <Polyline
            positions={polylinePoints}
            pathOptions={{ color: "#1B5E97", weight: 5, opacity: 0.85 }}
          />
        )}

        {/* Промежуточные точки — буквенные маркеры */}
        {waypoints?.map((wp) => (
          <Marker
            key={`wp-${wp.id}`}
            position={[wp.lat, wp.lon]}
            icon={L.divIcon({
              className: "",
              html: `<div style="
                display:flex;align-items:center;justify-content:center;
                width:24px;height:24px;border-radius:50%;
                background:#E67E22;color:#fff;font-size:11px;font-weight:700;
                border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.3);
              ">${wp.label}</div>`,
              iconSize: [24, 24],
              iconAnchor: [12, 12],
            })}
          >
            <Popup>
              <strong>{wp.label}. {wp.name}</strong>
              <br />
              {wp.lat.toFixed(5)}, {wp.lon.toFixed(5)}
            </Popup>
          </Marker>
        ))}

        {/* Подсвеченные остановки (вдоль маршрута) — крупными маркерами */}
        {highlightedStops?.map((s, idx) => (
          <Marker key={`hl-${s.id}`} position={[Number(s.lat), Number(s.lon)]}>
            <Popup>
              <strong>#{idx + 1}. {s.name}</strong>
              <br />
              {Number(s.lat).toFixed(5)}, {Number(s.lon).toFixed(5)}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
