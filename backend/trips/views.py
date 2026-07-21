from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import TripRequestSerializer
from .models import Trip
from . import routing
from .hos_engine import simulate_trip
from .log_builder import build_daily_logs


STATUS_LABELS = {
    "off_duty": "Off Duty",
    "sleeper": "Sleeper Berth",
    "driving": "Driving",
    "on_duty": "On Duty (Not Driving)",
}


@api_view(["POST"])
def plan_trip(request):
    serializer = TripRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        current = routing.geocode(data["current_location"])
        pickup = routing.geocode(data["pickup_location"])
        dropoff = routing.geocode(data["dropoff_location"])
    except routing.RoutingError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    try:
        leg1 = routing.route([(current[0], current[1]), (pickup[0], pickup[1])])
        leg2 = routing.route([(pickup[0], pickup[1]), (dropoff[0], dropoff[1])])
    except routing.RoutingError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    segments = simulate_trip(
        drive_to_pickup_hr=leg1["duration_hours"],
        miles_to_pickup=leg1["distance_miles"],
        drive_to_dropoff_hr=leg2["duration_hours"],
        miles_to_dropoff=leg2["distance_miles"],
        cycle_hours_used=data["cycle_hours_used"],
    )

    daily_logs = build_daily_logs(segments)

    total_driving = sum(s.hours for s in segments if s.status == "driving")
    total_on_duty = sum(s.hours for s in segments if s.status == "on_duty")
    total_off_duty = sum(s.hours for s in segments if s.status == "off_duty")
    num_resets = sum(
        1 for s in segments
        if s.status == "off_duty" and ("reset" in s.label.lower() or "restart" in s.label.lower())
    )
    num_breaks = sum(
        1 for s in segments if s.status == "off_duty" and "break" in s.label.lower()
    )
    num_fuel_stops = sum(1 for s in segments if "fuel" in s.label.lower())

    result = {
        "locations": {
            "current": {"name": current[2], "lat": current[0], "lon": current[1]},
            "pickup": {"name": pickup[2], "lat": pickup[0], "lon": pickup[1]},
            "dropoff": {"name": dropoff[2], "lat": dropoff[0], "lon": dropoff[1]},
        },
        "route": {
            "to_pickup": {
                "distance_miles": leg1["distance_miles"],
                "duration_hours": round(leg1["duration_hours"], 2),
                "geometry": leg1["geometry"],
            },
            "to_dropoff": {
                "distance_miles": leg2["distance_miles"],
                "duration_hours": round(leg2["duration_hours"], 2),
                "geometry": leg2["geometry"],
            },
            "total_distance_miles": round(
                leg1["distance_miles"] + leg2["distance_miles"], 1
            ),
        },
        "summary": {
            "total_driving_hours": round(total_driving, 2),
            "total_on_duty_hours": round(total_on_duty, 2),
            "total_off_duty_hours": round(total_off_duty, 2),
            "num_days": len(daily_logs),
            "num_10hr_resets": num_resets,
            "num_30min_breaks": num_breaks,
            "num_fuel_stops": num_fuel_stops,
            "cycle_hours_used_at_start": data["cycle_hours_used"],
            "cycle_hours_used_at_end": round(
                (daily_logs[-1]["totals"]["driving"] + daily_logs[-1]["totals"]["on_duty"])
                if daily_logs else 0,
                2,
            ),
        },
        "stops": [
            {
                "label": STATUS_LABELS.get(s.status, s.status),
                "detail": s.label,
                "duration_hours": round(s.hours, 2),
            }
            for s in segments
            if s.label and s.status != "driving"
        ],
        "daily_logs": daily_logs,
    }

    Trip.objects.create(
        current_location=data["current_location"],
        pickup_location=data["pickup_location"],
        dropoff_location=data["dropoff_location"],
        cycle_hours_used=data["cycle_hours_used"],
        result=result,
    )

    return Response(result, status=status.HTTP_200_OK)
