# ResQMap - Emergency Disaster Management System 🚨

## Quick Start

### Backend Setup
```powershell
cd backend
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate
pip install -r requirements-minimal.txt
copy .env.example .env
python seed_data.py
python -m uvicorn app.main:app --reload
```

### Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```

### Login
- **Email**: `john.doe@emergency.gov`
- **Password**: `demo123`

---

## HERE Weather API Setup

### 1. Get API Key
1. Go to: https://platform.here.com/
2. Create project → Generate API Key
3. Copy your key

### 2. Add to `.env`
```bash
# backend/.env
HERE_API_KEY=your_actual_api_key_here
```

### 3. Restart Backend
```powershell
cd backend
python -m uvicorn app.main:app --reload
```

---

## LIVE Data Sources (HERE API)

### ✅ Integrated Features

| Feature | Endpoint | Description |
|---------|----------|-------------|
| **Weather Alerts** | `/api/weather/india-alerts` | Live storm/rain/cyclone warnings |
| **Traffic Incidents** | `/api/weather/india-traffic` | Accidents, closures, construction |
| **Current Weather** | `/api/weather/current` | Temp, wind, humidity |
| **7-Day Forecast** | `/api/weather/forecast` | Weather predictions |

### 🧪 Test LIVE Data

```bash
# 1. Open API docs
http://localhost:8000/docs

# 2. Try these endpoints:
GET /api/weather/india-alerts     # Weather warnings
GET /api/weather/india-traffic    # Traffic incidents
GET /api/weather/current           # Current weather
```

**Example: Weather Alerts**
```json
{
  "alerts": [
    {"title": "Heavy rain anticipated", "location": "Delhi", "severity": "High"},
    {"title": "Heavy rain anticipated", "location": "Chennai", "severity": "High"}
  ],
  "count": 4,
  "source": "live"
}
```

**Example: Traffic Incidents**
```json
{
  "incidents": [
    {"type": "Accident", "location": "Mumbai", "severity": "Critical"},
    {"type": "Road Closure", "location": "Delhi", "severity": "High"}
  ],
  "count": 8
}
```

---

## Dashboard Features

### What's LIVE (Real-time from HERE API)
- ✅ Weather alerts for 7 India cities
- ✅ Traffic incidents (accidents, closures)
- ✅ Current weather conditions
- ✅ Click "Refresh Data" to update

### What's from Database (Historical)
- 📝 Disaster impact reports
- 📝 Evacuation data
- 📝 Infrastructure damage
- 📝 Casualty reports

**Both complement each other!**

---

## Maps Page

### Layers Available
- **Damaged Zones** (Red) - Infrastructure damage areas
- **Flooded Areas** (Blue) - Water-affected regions
- **Displaced Population** (Markers) - Evacuation camps

### Active Incidents
- Shows India disaster data from database
- Cyclone in Gujarat, Floods in Mumbai/Assam
- Real coordinates for India locations

---

## India Locations (Demo Data)

| Location | Coordinates | Disaster Type |
|----------|-------------|---------------|
| Gujarat Coast | 23.0225°N, 70.1324°E | Cyclone |
| Mumbai | 19.0760°N, 72.8777°E | Monsoon Flood |
| Assam | 26.2006°N, 92.9376°E | River Flood |

---

## API Reference

### Weather Endpoints
```bash
GET /api/weather/current?latitude=19.0760&longitude=72.8777
GET /api/weather/forecast?latitude=19.0760&longitude=72.8777&days=7
GET /api/weather/india-alerts
GET /api/weather/severe-weather?latitude=19.0760&longitude=72.8777
```

### Traffic Endpoints
```bash
GET /api/weather/india-traffic
GET /api/weather/traffic-incidents?latitude=19.0760&longitude=72.8777&radius=50000
```

### Dashboard Endpoints
```bash
GET /api/dashboard/stats
GET /api/dashboard/recent-alerts?limit=5&source=database
```

### Maps Endpoints
```bash
GET /api/maps/layers
GET /api/maps/active-incidents
```

---

## Environment Variables

### Backend (`.env`)
```bash
# Database
DATABASE_URL=sqlite:///./resqmap.db

# Security
SECRET_KEY=your-secret-key-here

# HERE Weather API
HERE_API_KEY=your_here_api_key_here
HERE_BASE_URL=https://weather.cc.api.here.com/weather/1.0
```

### Frontend (optional)
```bash
VITE_API_URL=http://localhost:8000
```

---

## What's Changed

### ✅ Added
- LIVE weather alerts from HERE API
- LIVE traffic incidents (accidents, closures)
- India-specific seed data (Gujarat, Mumbai, Assam)
- Map centered on India
- Dynamic dashboard stats

### ❌ Removed
- Time evolution widget (not useful)
- Road status layer (not available from HERE)
- Export map button (non-functional)
- US/Florida demo data

---

## Troubleshooting

### "Weather API error: 401"
- Invalid API key
- Get new key from platform.here.com

### "No alerts showing"
- Check if HERE_API_KEY is in `.env`
- Restart backend after adding key

### "Map shows empty circles"
- Run `python seed_data.py` to add India data
- Restart backend

### "Dashboard shows no data"
- Backend not running
- Check: http://localhost:8000/docs

---

## Tech Stack

**Backend**: FastAPI, SQLite, SQLAlchemy
**Frontend**: React, TypeScript, Vite, TailwindCSS
**Maps**: Leaflet, OpenStreetMap
**APIs**: HERE Weather API, HERE Traffic API

---

## Free Tier Limits

- HERE API: 250,000 transactions/month
- Current usage: ~100 requests/day (well within limits)

---

## Quick Commands

```powershell
# Start backend
cd backend && python -m uvicorn app.main:app --reload

# Start frontend
cd frontend && npm run dev

# Reseed database with India data
cd backend && python seed_data.py

# Test API
http://localhost:8000/docs

# Access app
http://localhost:3000
```

---

## Support

For issues or questions, check:
- API Documentation: http://localhost:8000/docs
- HERE API Docs: https://www.here.com/docs/bundle/weather-api-developer-guide
- Backend logs in terminal

---

**You're all set! 🎉 Start with `python -m uvicorn app.main:app --reload` in backend and `npm run dev` in frontend.**
