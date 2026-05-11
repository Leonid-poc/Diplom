"use client";
import { useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
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

type Props = {
  stops?: Stop[];
  routePath?: Stop[];
  className?: string;
};

export default function LeafletMap({ stops, routePath, className }: Props) {
  // Защита от SSR (иногда модуль грузится дважды)
  useEffect(() => {
    return () => {
      /* cleanup if needed */
    };
  }, []);

  return (
    <div className={className ?? "h-[600px] w-full rounded-md overflow-hidden border"}>
      <MapContainer center={[CENTER_LAT, CENTER_LON]} zoom={ZOOM} scrollWheelZoom>
        <TileLayer url={TILE_URL} attribution={TILE_ATTR} />

        {stops?.map((s) => (
          <Marker key={s.id} position={[Number(s.lat), Number(s.lon)]}>
            <Popup>
              <strong>{s.name}</strong>
              <br />
              {Number(s.lat).toFixed(5)}, {Number(s.lon).toFixed(5)}
            </Popup>
          </Marker>
        ))}

        {routePath && routePath.length > 1 && (
          <Polyline
            positions={routePath.map((s) => [Number(s.lat), Number(s.lon)] as [number, number])}
            pathOptions={{ color: "#1B5E97", weight: 5 }}
          />
        )}
      </MapContainer>
    </div>
  );
}
