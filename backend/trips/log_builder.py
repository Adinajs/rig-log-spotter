"""
Takes the flat, chronological list of HOS Segments produced by hos_engine
and lays them onto a 24-hour clock, splitting any segment that crosses
midnight so each calendar day gets its own FMCSA-style daily log sheet.
"""
from datetime import datetime, timedelta

DEFAULT_START_HOUR = 6  # assume the driver clocks on at 06:00 on day 1


def build_daily_logs(segments, start_datetime=None, start_odometer=0):
    """Returns a list of day dicts:
    {
      "day_number": 1,
      "date": "2026-07-20",
      "entries": [{"status": "...", "start_hour": 6.0, "end_hour": 7.5,
                    "label": "..."}],
      "totals": {"off_duty": h, "sleeper": h, "driving": h, "on_duty": h},
      "miles_driven": m,
      "start_odometer": x, "end_odometer": y,
    }
    """
    if start_datetime is None:
        now = datetime.utcnow()
        start_datetime = now.replace(
            hour=DEFAULT_START_HOUR, minute=0, second=0, microsecond=0
        )

    days = []
    day_start = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)

    def get_day(dt):
        day_index = (dt.replace(hour=0, minute=0, second=0, microsecond=0) - day_start).days
        while len(days) <= day_index:
            d = day_start + timedelta(days=len(days))
            days.append({
                "day_number": len(days) + 1,
                "date": d.strftime("%Y-%m-%d"),
                "entries": [],
                "totals": {"off_duty": 0.0, "sleeper": 0.0, "driving": 0.0, "on_duty": 0.0},
                "miles_driven": 0.0,
            })
        return days[day_index]

    cursor = start_datetime
    odometer = start_odometer

    for seg in segments:
        remaining_hours = seg.hours
        seg_cursor = cursor
        while remaining_hours > 1e-6:
            midnight = (seg_cursor + timedelta(days=1)).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            hours_until_midnight = (midnight - seg_cursor).total_seconds() / 3600.0
            chunk_hours = min(remaining_hours, hours_until_midnight)
            chunk_miles = (
                seg.miles * (chunk_hours / seg.hours) if seg.hours > 0 else 0
            )

            day = get_day(seg_cursor)
            day_local_start = (
                seg_cursor - seg_cursor.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds() / 3600.0
            day_local_end = day_local_start + chunk_hours

            day["entries"].append({
                "status": seg.status,
                "start_hour": round(day_local_start, 3),
                "end_hour": round(day_local_end, 3),
                "label": seg.label,
            })
            day["totals"][seg.status] = round(
                day["totals"][seg.status] + chunk_hours, 3
            )
            if seg.status == "driving":
                day["miles_driven"] = round(day["miles_driven"] + chunk_miles, 1)

            seg_cursor = seg_cursor + timedelta(hours=chunk_hours)
            remaining_hours -= chunk_hours

        cursor = seg_cursor

    running_odo = start_odometer
    for day in days:
        day["start_odometer"] = round(running_odo, 1)
        running_odo += day["miles_driven"]
        day["end_odometer"] = round(running_odo, 1)

    return days
