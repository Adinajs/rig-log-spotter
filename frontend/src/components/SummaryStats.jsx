const STAT_CONFIG = [
  { key: "total_distance_miles", label: "Total distance", suffix: " mi", source: "route" },
  { key: "num_days", label: "Days on the road", suffix: "", source: "summary" },
  { key: "total_driving_hours", label: "Driving hours", suffix: " h", source: "summary" },
  { key: "num_10hr_resets", label: "10-hr / 34-hr resets", suffix: "", source: "summary" },
  { key: "num_30min_breaks", label: "30-min breaks", suffix: "", source: "summary" },
  { key: "num_fuel_stops", label: "Fuel stops", suffix: "", source: "summary" },
];

export default function SummaryStats({ result }) {
  return (
    <div className="summary-stats">
      {STAT_CONFIG.map((stat) => {
        const value =
          stat.source === "route" ? result.route[stat.key] : result.summary[stat.key];
        return (
          <div key={stat.key} className="summary-stats__item">
            <div className="summary-stats__value">
              {value}
              {stat.suffix}
            </div>
            <div className="summary-stats__label">{stat.label}</div>
          </div>
        );
      })}
    </div>
  );
}
