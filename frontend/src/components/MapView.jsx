import { MapContainer, TileLayer, Polyline, Marker, Popup, useMap } from "react-leaflet";
import L from "leaflet";
import { useEffect } from "react";

// Fix default marker icon paths (Vite/webpack asset handling breaks Leaflet's defaults)
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

function makeDotIcon(color) {
  return L.divIcon({
    className: "map-dot-icon",
    html: `<span style="background:${color}"></span>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
}

const CURRENT_ICON = makeDotIcon("var(--amber)");
const PICKUP_ICON = makeDotIcon("var(--green)");
const DROPOFF_ICON = makeDotIcon("var(--red)");

function FitBounds({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      map.fitBounds(positions, { padding: [40, 40] });
    }
  }, [positions, map]);
  return null;
}

export default function MapView({ result }) {
  const { locations, route } = result;

  const toPickupLine = route.to_pickup.geometry.map(([lon, lat]) => [lat, lon]);
  const toDropoffLine = route.to_dropoff.geometry.map(([lon, lat]) => [lat, lon]);
  const allPositions = [...toPickupLine, ...toDropoffLine];

  return (
    <div className="map-view">
      <MapContainer
        center={allPositions[0] || [39.5, -86]}
        zoom={6}
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={toPickupLine} pathOptions={{ color: "#ffb627", weight: 4 }} />
        <Polyline positions={toDropoffLine} pathOptions={{ color: "#4c9a6a", weight: 4 }} />

        <Marker position={[locations.current.lat, locations.current.lon]} icon={CURRENT_ICON}>
          <Popup>Current: {locations.current.name}</Popup>
        </Marker>
        <Marker position={[locations.pickup.lat, locations.pickup.lon]} icon={PICKUP_ICON}>
          <Popup>Pickup: {locations.pickup.name}</Popup>
        </Marker>
        <Marker position={[locations.dropoff.lat, locations.dropoff.lon]} icon={DROPOFF_ICON}>
          <Popup>Drop-off: {locations.dropoff.name}</Popup>
        </Marker>

        <FitBounds positions={allPositions} />
      </MapContainer>

      <div className="map-view__legend">
        <span><i className="legend-dot" style={{ background: "var(--amber)" }} /> Current</span>
        <span><i className="legend-dot" style={{ background: "var(--green)" }} /> Pickup</span>
        <span><i className="legend-dot" style={{ background: "var(--red)" }} /> Drop-off</span>
      </div>
    </div>
  );
}
