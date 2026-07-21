"""
Free, no-API-key routing and geocoding.

- Geocoding: OpenStreetMap Nominatim (https://nominatim.org)
- Routing:   OSRM public demo server (https://router.project-osrm.org)

Both are free public services intended for light/demo usage. No credentials
are required, which keeps this project deployable without any paid keys.
"""
import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

HEADERS = {"User-Agent": "spotter-eld-trip-planner/1.0 (assessment project)"}

MILES_PER_METER = 0.000621371
HOURS_PER_SECOND = 1 / 3600.0


class RoutingError(Exception):
    pass


def geocode(place_name: str):
    """Returns (lat, lon, display_name) for a free-text place name."""
    resp = requests.get(
        NOMINATIM_URL,
        params={"q": place_name, "format": "json", "limit": 1},
        headers=HEADERS,
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        raise RoutingError(f"Could not find a location matching '{place_name}'")
    top = results[0]
    return float(top["lat"]), float(top["lon"]), top.get("display_name", place_name)


def route(coords):
    """coords: list of (lat, lon) tuples, in order.
    Returns dict with total distance_miles, duration_hours, geometry (GeoJSON
    LineString coordinates as [lon, lat] pairs), and per-leg breakdown.
    """
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in coords)
    url = f"{OSRM_URL}/{coord_str}"
    resp = requests.get(
        url,
        params={"overview": "full", "geometries": "geojson"},
        headers=HEADERS,
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != "Ok" or not data.get("routes"):
        raise RoutingError("Could not compute a route between the given locations")

    r = data["routes"][0]
    legs = [
        {
            "distance_miles": round(leg["distance"] * MILES_PER_METER, 1),
            "duration_hours": round(leg["duration"] * HOURS_PER_SECOND, 3),
        }
        for leg in r["legs"]
    ]
    return {
        "distance_miles": round(r["distance"] * MILES_PER_METER, 1),
        "duration_hours": round(r["duration"] * HOURS_PER_SECOND, 3),
        "geometry": r["geometry"]["coordinates"],  # [lon, lat] pairs
        "legs": legs,
    }
