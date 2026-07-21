const ROW_ORDER = ["off_duty", "sleeper", "driving", "on_duty"];
const ROW_LABELS = {
  off_duty: "Off Duty",
  sleeper: "Sleeper Berth",
  driving: "Driving",
  on_duty: "On Duty\n(Not Driving)",
};
const ROW_COLORS = {
  off_duty: "#6b6355",
  sleeper: "#4c6b8a",
  driving: "#c1443c",
  on_duty: "#ab8a3a",
};

const LEFT_MARGIN = 168;
const RIGHT_MARGIN = 56;
const TOP_MARGIN = 34;
const ROW_HEIGHT = 42;
const CHART_WIDTH = 792; // 24 hours * 33px
const HOUR_WIDTH = CHART_WIDTH / 24;
const CHART_HEIGHT = ROW_HEIGHT * 4;
const SVG_WIDTH = LEFT_MARGIN + CHART_WIDTH + RIGHT_MARGIN;
const SVG_HEIGHT = TOP_MARGIN + CHART_HEIGHT + 30;

function rowY(statusIndex) {
  return TOP_MARGIN + statusIndex * ROW_HEIGHT;
}

function xForHour(hour) {
  return LEFT_MARGIN + hour * HOUR_WIDTH;
}

function buildPath(entries) {
  if (entries.length === 0) return "";
  const sorted = [...entries].sort((a, b) => a.start_hour - b.start_hour);
  let d = "";
  let prevY = null;
  sorted.forEach((entry, i) => {
    const rowIdx = ROW_ORDER.indexOf(entry.status);
    const y = rowY(rowIdx) + ROW_HEIGHT / 2;
    const x1 = xForHour(entry.start_hour);
    const x2 = xForHour(entry.end_hour);
    if (i === 0) {
      d += `M ${x1} ${y} `;
    } else if (prevY !== y) {
      d += `L ${x1} ${prevY} L ${x1} ${y} `;
    }
    d += `L ${x2} ${y} `;
    prevY = y;
  });
  return d;
}

export default function LogSheetGrid({ day }) {
  const path = buildPath(day.entries);
  const totals = day.totals;

  return (
    <div className="log-sheet">
      <div className="log-sheet__header">
        <div>
          <div className="log-sheet__day">Day {day.day_number}</div>
          <div className="log-sheet__date">{day.date}</div>
        </div>
        <div className="log-sheet__odo">
          <span>Start odometer</span>
          <strong>{day.start_odometer.toLocaleString()} mi</strong>
        </div>
        <div className="log-sheet__odo">
          <span>End odometer</span>
          <strong>{day.end_odometer.toLocaleString()} mi</strong>
        </div>
        <div className="log-sheet__odo">
          <span>Miles today</span>
          <strong>{day.miles_driven.toLocaleString()} mi</strong>
        </div>
      </div>

      <svg
        viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`}
        width="100%"
        role="img"
        aria-label={`Daily log grid for day ${day.day_number}, ${day.date}`}
      >
        {/* hour tick labels */}
        {Array.from({ length: 25 }).map((_, h) => (
          <text
            key={h}
            x={xForHour(h)}
            y={TOP_MARGIN - 12}
            fontSize="9"
            fontFamily="var(--font-mono)"
            fill="var(--text-on-paper-dim)"
            textAnchor="middle"
          >
            {h % 24}
          </text>
        ))}

        {/* vertical hour/quarter-hour rules */}
        {Array.from({ length: 25 }).map((_, h) => (
          <line
            key={`hr-${h}`}
            x1={xForHour(h)}
            x2={xForHour(h)}
            y1={TOP_MARGIN}
            y2={TOP_MARGIN + CHART_HEIGHT}
            stroke="var(--paper-line)"
            strokeWidth={h % 6 === 0 ? 1.4 : 0.8}
          />
        ))}
        {Array.from({ length: 96 }).map((_, q) => (
          <line
            key={`q-${q}`}
            x1={xForHour(q / 4)}
            x2={xForHour(q / 4)}
            y1={TOP_MARGIN}
            y2={TOP_MARGIN + CHART_HEIGHT}
            stroke="var(--paper-line)"
            strokeWidth={0.4}
          />
        ))}

        {/* row lanes + labels */}
        {ROW_ORDER.map((status, i) => (
          <g key={status}>
            <rect
              x={LEFT_MARGIN}
              y={rowY(i)}
              width={CHART_WIDTH}
              height={ROW_HEIGHT}
              fill={i % 2 === 0 ? "rgba(35,32,26,0.03)" : "transparent"}
              stroke="var(--paper-line)"
            />
            {ROW_LABELS[status].split("\n").map((line, li) => (
              <text
                key={li}
                x={LEFT_MARGIN - 12}
                y={rowY(i) + ROW_HEIGHT / 2 + li * 11 - (ROW_LABELS[status].includes("\n") ? 4 : 0)}
                fontSize="11"
                fontFamily="var(--font-body)"
                fontWeight="600"
                fill="var(--text-on-paper)"
                textAnchor="end"
              >
                {line}
              </text>
            ))}
            <text
              x={SVG_WIDTH - RIGHT_MARGIN + 10}
              y={rowY(i) + ROW_HEIGHT / 2 + 4}
              fontSize="12"
              fontFamily="var(--font-mono)"
              fontWeight="600"
              fill={ROW_COLORS[status]}
            >
              {totals[status].toFixed(1)}h
            </text>
          </g>
        ))}

        {/* duty status line, drawn like pen on paper */}
        <path
          d={path}
          fill="none"
          stroke="#23201a"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        <line
          x1={LEFT_MARGIN}
          x2={LEFT_MARGIN}
          y1={TOP_MARGIN}
          y2={TOP_MARGIN + CHART_HEIGHT}
          stroke="var(--text-on-paper)"
          strokeWidth="1.4"
        />
      </svg>

      <div className="log-sheet__remarks">
        {day.entries.map((entry, i) => (
          <span key={i} className="log-sheet__remark-chip" style={{ borderColor: ROW_COLORS[entry.status] }}>
            {entry.label || ROW_LABELS[entry.status].replace("\n", " ")}
            <em>{formatClock(entry.start_hour)}–{formatClock(entry.end_hour)}</em>
          </span>
        ))}
      </div>
    </div>
  );
}

function formatClock(hourFloat) {
  const h = Math.floor(hourFloat) % 24;
  const m = Math.round((hourFloat - Math.floor(hourFloat)) * 60);
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}
