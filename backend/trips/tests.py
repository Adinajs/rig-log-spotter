from django.test import TestCase
from .hos_engine import simulate_trip
from .log_builder import build_daily_logs


class HOSEngineTests(TestCase):
    def test_short_trip_no_reset_needed(self):
        # 2 hrs to pickup, 3 hrs to dropoff, fresh cycle -> should all fit
        # in one shift, only pickup/dropoff on-duty time added.
        segments = simulate_trip(2.0, 100, 3.0, 150, cycle_hours_used=0)
        total_drive = sum(s.hours for s in segments if s.status == "driving")
        self.assertAlmostEqual(total_drive, 5.0, places=2)
        # No resets should be needed for such a short trip
        resets = [s for s in segments if "reset" in s.label.lower()]
        self.assertEqual(len(resets), 0)

    def test_long_trip_triggers_break_after_8_hours(self):
        # 10 hours of continuous driving should trigger a 30 min break
        segments = simulate_trip(10.0, 600, 0.0, 0, cycle_hours_used=0)
        breaks = [s for s in segments if "break" in s.label.lower()]
        self.assertGreaterEqual(len(breaks), 1)

    def test_daily_drive_limit_triggers_reset(self):
        # 13 hours driving exceeds the 11-hour daily limit -> must trigger
        # a 10-hour reset somewhere in the segments.
        segments = simulate_trip(13.0, 700, 0.0, 0, cycle_hours_used=0)
        resets = [s for s in segments if "reset" in s.label.lower()]
        self.assertGreaterEqual(len(resets), 1)
        total_drive = sum(s.hours for s in segments if s.status == "driving")
        self.assertAlmostEqual(total_drive, 13.0, places=1)

    def test_cycle_limit_respected(self):
        # Starting with 68 hours already used in the cycle, only 2 more
        # hours of on-duty/driving time are available before a restart.
        segments = simulate_trip(5.0, 300, 0.0, 0, cycle_hours_used=68)
        restarts = [
            s for s in segments
            if s.status == "off_duty" and ("reset" in s.label.lower() or "restart" in s.label.lower())
        ]
        self.assertGreaterEqual(len(restarts), 1)

    def test_fuel_stop_inserted_over_1000_miles(self):
        segments = simulate_trip(20.0, 1200, 0.0, 0, cycle_hours_used=0)
        fuel_stops = [s for s in segments if "fuel" in s.label.lower()]
        self.assertGreaterEqual(len(fuel_stops), 1)

    def test_daily_logs_split_across_midnight(self):
        segments = simulate_trip(13.0, 700, 2.0, 100, cycle_hours_used=0)
        logs = build_daily_logs(segments)
        self.assertGreater(len(logs), 1)
        for day in logs:
            for entry in day["entries"]:
                self.assertGreaterEqual(entry["start_hour"], 0)
                self.assertLessEqual(entry["end_hour"], 24.0001)
