import { useState } from "react";
import TripForm from "./components/TripForm.jsx";
import MapView from "./components/MapView.jsx";
import SummaryStats from "./components/SummaryStats.jsx";
import LogSheetGrid from "./components/LogSheetGrid.jsx";
import { planTrip } from "./api.js";
import "./App.css";

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(values) {
    setLoading(true);
    setError(null);
    try {
      const data = await planTrip(values);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to plan trip.");
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__brand">
          <span className="app__brand-mark">RL</span>
          <div>
            <div className="app__brand-name">Rig Log</div>
            <div className="app__brand-tagline">Trip &amp; HOS compliance planner</div>
          </div>
        </div>
      </header>

      <main className="app__main">
        <section className="app__intro">
          <h1>Plan a route. Get compliant logs.</h1>
          <p>
            Enter a trip and Rig Log maps the route, schedules every required
            break, fuel stop, and 10-hour reset under the 70-hr/8-day cycle,
            then draws out the daily log sheets for you.
          </p>
        </section>

        <TripForm onSubmit={handleSubmit} loading={loading} />

        {error && <div className="app__error">{error}</div>}

        {loading && (
          <div className="app__loading">
            <div className="spinner" />
            Calculating route and duty schedule…
          </div>
        )}

        {result && !loading && (
          <>
            <SummaryStats result={result} />

            <section className="app__section">
              <h2>Route</h2>
              <MapView result={result} />
            </section>

            <section className="app__section">
              <h2>Daily log sheets</h2>
              <div className="log-sheet-stack">
                {result.daily_logs.map((day) => (
                  <LogSheetGrid key={day.day_number} day={day} />
                ))}
              </div>
            </section>
          </>
        )}
      </main>

      <footer className="app__footer">
        Built for the Spotter AI full-stack assessment. Routing via OSRM
        &amp; OpenStreetMap Nominatim.
      </footer>
    </div>
  );
}
