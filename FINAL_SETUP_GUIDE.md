# ResQMap - Complete Setup & Testing Guide 🇮🇳


## What You're Getting:
- 🚨 **Accidents** - Real-time from traffic sensors
- 🚧 **Road Closures** - Construction and maintenance
- 🏗️ **Construction Zones** - Active work areas
- 🚦 **Traffic Jams** - Congestion alerts

## 📋 Complete Feature List

### ✅ Working Features (LIVE Data)

| Feature | Status | Data Source |
|---------|--------|-------------|
| Weather Alerts | ✅ **LIVE** | HERE Weather API |
| Traffic Incidents | ✅ **LIVE** | HERE Traffic API |
| Current Weather | ✅ **LIVE** | HERE Weather API |
| 7-Day Forecast | ✅ **LIVE** | HERE Weather API |
| Dashboard Stats | ✅ Dynamic | Database |
| Active Incidents Map | ✅ India Data | Database |
| Damaged Zones Map | ✅ India Data | Database |
| Flooded Areas Map | ✅ India Data | Database |


## 🔄 Complete Testing Checklist

### 1. Backend Health
```bash
# Check backend is running
http://localhost:8000/docs
```

### 2. Dashboard
```bash
# Go to
http://localhost:3000/dashboard

# You should see:
✓ LIVE weather alerts (Delhi, Chennai, Kolkata, Assam)
✓ Stats updating when you click "Refresh Data"
✓ "LIVE - HERE Weather API" source tag on alerts
```

### 3. Maps Page
```bash
# Go to
http://localhost:3000/maps

# You should see:
✓ Map centered on India (20.59°N, 78.96°E)
✓ Active Incidents showing:
  - Cyclone Biparjoy Approaching Gujarat Coast
  - Severe Monsoon Flooding - Mumbai
  - Flood Alert - Brahmaputra River Rising
✓ All India locations (no Florida/US data)
```

### 4. Weather Alerts
```bash
# In API docs:
GET /api/weather/india-alerts

# Should return:
✓ 4+ weather alerts for India cities
✓ Real-time warnings (heavy rain, etc.)
✓ "source": "live"
```

### 5. Traffic Incidents
```bash
# In API docs:
GET /api/weather/india-traffic

# Should return:
✓ Traffic incidents for Mumbai, Delhi, Bangalore, Chennai
✓ Accident types, road closures, construction
✓ Verified incidents from HERE traffic sensors
```

---

## 🚀 Quick Start Commands

### First Time Setup:
```powershell
# Backend
cd backend
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate
pip install -r requirements-minimal.txt
copy .env.example .env
# Add your HERE_API_KEY to .env
python seed_data.py
python -m uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Access: http://localhost:3000
# Login: john.doe@emergency.gov / demo123
```

### Daily Development:
```powershell
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 📊 Data Flow

```
┌─────────────────────────────────────────┐
│         LIVE DATA (Real-time)           │
├─────────────────────────────────────────┤
│ HERE Weather API                        │
│ • Weather alerts (storms, rain)         │
│ • Traffic incidents (accidents)         │
│ • Current weather (temp, wind)          │
│ • 7-day forecast                        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│        YOUR BACKEND API                 │
├─────────────────────────────────────────┤
│ FastAPI endpoints process & format     │
│ data for frontend consumption          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│         DASHBOARD UI                    │
├─────────────────────────────────────────┤
│ • Shows LIVE weather alerts             │
│ • Displays stats from database          │
│ • "Refresh Data" button updates        │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│      DATABASE (Historical)              │
├─────────────────────────────────────────┤
│ SQLite                                  │
│ • Disaster impact reports               │
│ • Evacuation/damage data                │
│ • Infrastructure assessments            │
│ • India-specific seed data              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│           MAPS PAGE                     │
├─────────────────────────────────────────┤
│ • Active Incidents (India disasters)    │
│ • Damaged Zones (red circles)           │
│ • Flooded Areas (blue circles)          │
│ • Displaced Population (markers)        │
└─────────────────────────────────────────┘
```

## 🆘 Troubleshooting

### "Active Incidents still shows US data"
```powershell
# Restart backend to apply changes:
cd backend
python -m uvicorn app.main:app --reload
```

### "Dashboard shows no weather alerts"
```bash
# Check HERE_API_KEY in backend/.env
# Restart backend after adding
```

### "Traffic incidents returns empty array"
```bash
# This is normal if there are no current incidents
# HERE API returns only active traffic events
# Try different times of day (rush hour = more incidents)
```

### "Map doesn't show India locations"
```powershell
# Reseed database with India data:
cd backend
python seed_data.py
# Restart backend
```

---

## ✅ Final Checklist

Before considering setup complete, verify:

- [ ] Backend runs without errors on :8000
- [ ] Frontend runs without errors on :3000
- [ ] Login works (john.doe@emergency.gov / demo123)
- [ ] Dashboard shows LIVE weather alerts (not database alerts)
- [ ] Maps page shows India locations (Gujarat, Mumbai, Assam)
- [ ] Active Incidents sidebar shows Indian disasters
- [ ] No "Florida Keys" or "Louisiana" anywhere
- [ ] Traffic incidents API returns data (test in /docs)
- [ ] "Refresh Data" button works on dashboard
- [ ] Map layers toggle properly (Damaged Zones, Flooded Areas, Displaced)

---

## 📝 Summary

**ResQMap is now fully functional with:**
- 🌦️ LIVE weather alerts from HERE API for India
- 🚗 LIVE traffic incidents (accidents, closures)
- 🗺️ India-focused disaster data (Gujarat, Mumbai, Assam)
- 🧹 Clean UI (removed non-functional features)
- 📚 2 comprehensive documentation files
