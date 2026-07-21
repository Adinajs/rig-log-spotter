"""
Hours of Service (HOS) simulation engine.

Implements the FMCSA property-carrying driver ruleset assumed for this
assessment:
  - 70 hours / 8 days cycle limit (on-duty + driving)
  - 11-hour driving limit per shift
  - 14-hour on-duty window per shift (clock runs regardless of duty status)
  - 30-minute break required after 8 cumulative hours of driving
  - 10 consecutive hours off-duty required to start a new shift
  - 1 hour on-duty (not driving) for pickup, 1 hour for drop-off
  - Fuel stop (30 min, on-duty) at least once every 1,000 miles

This is a simulation, not a certified compliance engine -- it is built to
produce realistic, explainable stop/rest scheduling and log-sheet data for
a trip-planning demo app.
"""
from dataclasses import dataclass, field

DAILY_DRIVE_LIMIT = 11.0
DAILY_WINDOW_LIMIT = 14.0
BREAK_AFTER_DRIVE_HOURS = 8.0
BREAK_DURATION = 0.5
RESET_DURATION = 10.0
CYCLE_RESTART_DURATION = 34.0
CYCLE_LIMIT = 70.0
FUEL_INTERVAL_MILES = 1000.0
FUEL_STOP_DURATION = 0.5
PICKUP_DURATION = 1.0
DROPOFF_DURATION = 1.0

STATUS_OFF_DUTY = "off_duty"
STATUS_SLEEPER = "sleeper"
STATUS_DRIVING = "driving"
STATUS_ON_DUTY = "on_duty"


@dataclass
class Segment:
    status: str
    hours: float
    label: str = ""
    miles: float = 0.0


@dataclass
class SimState:
    cycle_used: float = 0.0
    day_drive: float = 0.0
    day_window: float = 0.0
    drive_since_break: float = 0.0
    shift_active: bool = False
    miles_since_fuel: float = 0.0
    segments: list = field(default_factory=list)


class HOSEngine:
    """Simulates a trip and produces an ordered list of Segments."""

    def __init__(self, cycle_hours_used: float):
        self.state = SimState(cycle_used=cycle_hours_used)

    # -- internal helpers -------------------------------------------------
    def _start_shift_if_needed(self):
        s = self.state
        if not s.shift_active:
            s.shift_active = True
            s.day_drive = 0.0
            s.day_window = 0.0
            s.drive_since_break = 0.0

    def _do_reset(self):
        s = self.state
        s.segments.append(Segment(STATUS_OFF_DUTY, RESET_DURATION, "10-hr off-duty reset"))
        s.shift_active = False
        s.day_drive = 0.0
        s.day_window = 0.0
        s.drive_since_break = 0.0

    def _do_cycle_restart(self):
        s = self.state
        s.segments.append(Segment(STATUS_OFF_DUTY, CYCLE_RESTART_DURATION, "34-hr restart (70-hr cycle reached)"))
        s.shift_active = False
        s.day_drive = 0.0
        s.day_window = 0.0
        s.drive_since_break = 0.0
        s.cycle_used = 0.0

    def _do_break(self):
        s = self.state
        s.segments.append(Segment(STATUS_OFF_DUTY, BREAK_DURATION, "30-min break"))
        s.drive_since_break = 0.0
        s.day_window += BREAK_DURATION

    def _do_fuel_stop(self):
        s = self.state
        s.segments.append(Segment(STATUS_ON_DUTY, FUEL_STOP_DURATION, "Fuel stop"))
        s.day_window += FUEL_STOP_DURATION
        s.cycle_used += FUEL_STOP_DURATION
        s.miles_since_fuel = 0.0

    # -- public API ---------------------------------------------------------
    def drive(self, hours_needed: float, miles: float, label: str):
        """Drive `hours_needed` hours covering `miles`, inserting breaks,
        fuel stops, and 10-hr resets wherever HOS limits require them."""
        s = self.state
        remaining = hours_needed
        miles_per_hour = miles / hours_needed if hours_needed > 0 else 0

        while remaining > 1e-6:
            self._start_shift_if_needed()

            avail_drive = DAILY_DRIVE_LIMIT - s.day_drive
            avail_window = DAILY_WINDOW_LIMIT - s.day_window
            avail_break = BREAK_AFTER_DRIVE_HOURS - s.drive_since_break
            avail_cycle = CYCLE_LIMIT - s.cycle_used

            if avail_break <= 1e-6:
                self._do_break()
                continue
            if avail_cycle <= 1e-6:
                self._do_cycle_restart()
                continue
            if avail_drive <= 1e-6 or avail_window <= 1e-6:
                self._do_reset()
                continue

            chunk = min(remaining, avail_drive, avail_window, avail_break, avail_cycle)
            chunk_miles = miles_per_hour * chunk

            s.segments.append(Segment(STATUS_DRIVING, chunk, label, miles=chunk_miles))
            s.day_drive += chunk
            s.day_window += chunk
            s.drive_since_break += chunk
            s.cycle_used += chunk
            s.miles_since_fuel += chunk_miles
            remaining -= chunk

            if s.miles_since_fuel >= FUEL_INTERVAL_MILES and remaining > 1e-6:
                self._do_fuel_stop()

    def on_duty(self, hours: float, label: str):
        s = self.state
        self._start_shift_if_needed()
        avail_window = DAILY_WINDOW_LIMIT - s.day_window
        avail_cycle = CYCLE_LIMIT - s.cycle_used
        if hours > avail_cycle + 1e-6:
            self._do_cycle_restart()
            self._start_shift_if_needed()
        elif hours > avail_window + 1e-6:
            self._do_reset()
            self._start_shift_if_needed()
        s.segments.append(Segment(STATUS_ON_DUTY, hours, label))
        s.day_window += hours
        s.cycle_used += hours

    def segments(self):
        return self.state.segments


def simulate_trip(drive_to_pickup_hr, miles_to_pickup, drive_to_dropoff_hr,
                   miles_to_dropoff, cycle_hours_used):
    """Run the full trip simulation: current -> pickup -> dropoff.

    Returns a list of Segment objects in chronological order.
    """
    engine = HOSEngine(cycle_hours_used=cycle_hours_used)
    if drive_to_pickup_hr > 0:
        engine.drive(drive_to_pickup_hr, miles_to_pickup, "En route to pickup")
    engine.on_duty(PICKUP_DURATION, "At pickup location")
    engine.drive(drive_to_dropoff_hr, miles_to_dropoff, "En route to drop-off")
    engine.on_duty(DROPOFF_DURATION, "At drop-off location")
    return engine.segments()
