import { useState } from "react";

const FIELD_CONFIG = [
  { key: "currentLocation", label: "Current location", placeholder: "e.g. Chicago, IL" },
  { key: "pickupLocation", label: "Pickup location", placeholder: "e.g. Indianapolis, IN" },
  { key: "dropoffLocation", label: "Drop-off location", placeholder: "e.g. Columbus, OH" },
];

export default function TripForm({ onSubmit, loading }) {
  const [values, setValues] = useState({
    currentLocation: "",
    pickupLocation: "",
    dropoffLocation: "",
    cycleHoursUsed: "",
  });
  const [error, setError] = useState(null);

  function update(key, value) {
    setValues((v) => ({ ...v, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    if (!values.currentLocation || !values.pickupLocation || !values.dropoffLocation) {
      setError("All three locations are required.");
      return;
    }
    const cycle = Number(values.cycleHoursUsed);
    if (Number.isNaN(cycle) || cycle < 0 || cycle > 70) {
      setError("Current cycle used must be a number between 0 and 70.");
      return;
    }
    onSubmit(values);
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <div className="trip-form__grid">
        {FIELD_CONFIG.map((field) => (
          <label key={field.key} className="trip-form__field">
            <span className="trip-form__label">{field.label}</span>
            <input
              type="text"
              value={values[field.key]}
              placeholder={field.placeholder}
              onChange={(e) => update(field.key, e.target.value)}
              autoComplete="off"
            />
          </label>
        ))}
        <label className="trip-form__field trip-form__field--narrow">
          <span className="trip-form__label">Current cycle used (hrs)</span>
          <input
            type="number"
            min={0}
            max={70}
            step={0.5}
            value={values.cycleHoursUsed}
            placeholder="0–70"
            onChange={(e) => update("cycleHoursUsed", e.target.value)}
          />
        </label>
      </div>

      {error && <div className="trip-form__error">{error}</div>}

      <button type="submit" className="trip-form__submit" disabled={loading}>
        {loading ? "Plotting route…" : "Plan trip"}
      </button>

      <p className="trip-form__assumptions">
        Assumes a property-carrying driver on the 70-hr/8-day cycle, no adverse
        driving conditions, fueling at least every 1,000 miles, and 1 hour
        each for pickup and drop-off.
      </p>
    </form>
  );
}
