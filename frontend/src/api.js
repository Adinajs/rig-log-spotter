const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function planTrip({ currentLocation, pickupLocation, dropoffLocation, cycleHoursUsed }) {
  const resp = await fetch(`${API_BASE}/api/trips/plan/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      current_location: currentLocation,
      pickup_location: pickupLocation,
      dropoff_location: dropoffLocation,
      cycle_hours_used: Number(cycleHoursUsed),
    }),
  });

  if (!resp.ok) {
    let detail = "Something went wrong planning this trip.";
    try {
      const body = await resp.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore parse errors, use default message
    }
    throw new Error(detail);
  }

  return resp.json();
}
