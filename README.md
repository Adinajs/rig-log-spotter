# Rig Log — Trip & HOS Compliance Planner 🚚

A full-stack app for property-carrying truck drivers: enter a trip (current location, pickup, drop-off, and current cycle hours used), and it returns a route map plus auto-generated FMCSA daily log sheets, fully compliant with the 70-hr/8-day HOS ruleset.

Built for the Spotter AI full-stack developer assessment.

## Live Demo 🌐
- **Frontend App:** [https://rig-log-spotter.vercel.app](https://rig-log-spotter.vercel.app)
- **Backend API:** [https://rig-log-spotter-production.up.railway.app](https://rig-log-spotter-production.up.railway.app)

## Stack 🛠️

- **Backend:** Django 6 + Django REST Framework. Free routing/geocoding via OSRM + OpenStreetMap Nominatim (no API keys required).
- **Frontend:** React (Vite) + Leaflet for the map, hand-rolled SVG for the daily log sheet grid.
- **Database:** SQLite locally, Postgres in production.

## How it works ⚙️

1. The frontend sends the 4 inputs to `POST /api/trips/plan/`.
2. The backend geocodes all three locations (Nominatim), then requests two route legs from OSRM: current → pickup, pickup → drop-off.
3. `trips/hos_engine.py` simulates the trip hour-by-hour against the HOS ruleset (11-hr driving limit, 14-hr on-duty window, 30-min break after 8 hrs driving, 10-hr resets, 34-hr restart at the 70-hr cycle limit, fuel stop every 1,000 mi, 1 hr each for pickup/drop-off), producing an ordered list of duty-status segments.
4. `trips/log_builder.py` lays those segments onto a 24-hour clock, splitting anything that crosses midnight so each calendar day becomes its own log sheet.
5. The frontend renders the route on a Leaflet map and draws each day's log as an SVG grid modeled on the real FMCSA daily log form.

See `backend/trips/tests.py` for unit tests covering the HOS engine (short trips, forced breaks, daily-limit resets, cycle-limit restarts, fuel stops, and midnight-crossing log splits) — all passing.

## Local development 💻

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver      # http://localhost:8000
```

Run tests: `python manage.py test trips`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local        # VITE_API_BASE_URL=http://localhost:8000
npm run dev                       # http://localhost:5173
```

## Deployment 🚀

### Backend → Railway

The backend is deployed to Railway with a PostgreSQL database. 
- API URL: `https://rig-log-spotter-production.up.railway.app`
- The `Procfile` handles running `manage.py migrate` and `collectstatic` upon release.

### Frontend → Vercel

The frontend is deployed to Vercel as a Vite application.
- App URL: `https://rig-log-spotter.vercel.app`
- Environment variable `VITE_API_BASE_URL` is set to point to the Railway backend.

## Project layout 📁

```text
backend/
  config/            Django project settings/urls
  trips/
    hos_engine.py     HOS simulation engine (the core logic)
    log_builder.py     Lays segments onto calendar-day log sheets
    routing.py          OSRM + Nominatim integration
    views.py             POST /api/trips/plan/
    tests.py              Unit tests for the HOS engine
frontend/
  src/
    components/
      TripForm.jsx        Trip input form
      MapView.jsx           Leaflet route map
      LogSheetGrid.jsx       SVG-rendered FMCSA daily log sheet
      SummaryStats.jsx        Trip summary stat strip
    api.js                     Backend API client
    App.jsx
```

## Assumptions (per assessment spec) 📋

- Property-carrying driver, 70-hr/8-day cycle, no adverse driving conditions.
- Fueling at least once every 1,000 miles.
- 1 hour each for pickup and drop-off, logged as on-duty (not driving).
