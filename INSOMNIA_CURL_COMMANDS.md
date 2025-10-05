# ResQMap - cURL Commands for Insomnia 🌐

## 📋 All LIVE Data from HERE API

Your ResQMap is now fetching **4 types of LIVE data** from HERE API:

1. **Weather Alerts** (storms, rain, cyclones)
2. **Traffic Incidents** (accidents, road closures)
3. **Current Weather** (temperature, wind, humidity)
4. **7-Day Forecast** (weather predictions)

---

## 🔑 API Key
```
e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA
```

---

## 1️⃣ Weather Alerts (What Your App Uses)

### Mumbai Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=19.0760&longitude=72.8777"
```

### Delhi Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=28.6139&longitude=77.2090"
```

### Chennai Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=13.0827&longitude=80.2707"
```

### Gujarat Coast Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=23.0225&longitude=70.1324"
```

### Kolkata Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=22.5726&longitude=88.3639"
```

### Bangalore Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=12.9716&longitude=77.5946"
```

### Assam Weather Alerts
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=26.2006&longitude=92.9376"
```

---

## 2️⃣ Traffic Incidents (What Your App Uses)

### Mumbai Traffic (30km radius)
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:19.0760,72.8777;r=30000&locationReferencing=none"
```

### Delhi Traffic (30km radius)
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:28.6139,77.2090;r=30000&locationReferencing=none"
```

### Bangalore Traffic (30km radius)
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:12.9716,77.5946;r=30000&locationReferencing=none"
```

### Chennai Traffic (30km radius)
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:13.0827,80.2707;r=30000&locationReferencing=none"
```

---

## 3️⃣ Current Weather (What Your App Uses)

### Mumbai Current Weather
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=observation&oneobservation=true&latitude=19.0760&longitude=72.8777"
```

### Delhi Current Weather
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=observation&oneobservation=true&latitude=28.6139&longitude=77.2090"
```

### Chennai Current Weather
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=observation&oneobservation=true&latitude=13.0827&longitude=80.2707"
```

---

## 4️⃣ Traffic Incidents API (What Your App Uses)

### Mumbai Traffic Incidents
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:19.0760,72.8777;r=30000&locationReferencing=none"
```

### Chennai Traffic Incidents
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:13.0827,80.2707;r=30000&locationReferencing=none"
```

### Delhi Traffic Incidents
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:28.6139,77.2090;r=30000&locationReferencing=none"
```

### Kolkata Traffic Incidents
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:22.5726,88.3639;r=30000&locationReferencing=none"
```

### Bangalore Traffic Incidents
```bash
curl -X GET "https://data.traffic.hereapi.com/v7/incidents?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&in=circle:12.9716,77.5946;r=30000&locationReferencing=none"
```

**Key Fields in Response:**
```json
{
  "results": [{
    "incidentDetails": {
      "id": "...",
      "typeDescription": { "value": "Road closure" },
      "description": { "value": "At Bandra Kurla Complex Road - Closed" },
      "criticality": "critical",
      "roadClosed": true,
      "startTime": "2025-10-05T10:30:00Z"
    }
  }]
}
```

---

## 5️⃣ Weather Impact Analysis (Combined API - Your Dashboard)

### Get Weather Impact for All Cities
```bash
curl -X GET "http://localhost:8000/api/weather/impact-analysis" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "temperature_range": { "min": 28.2, "max": 33.6, "avg": 30.5 },
  "humidity": 72.2,
  "rain_alerts": 3,
  "critical_zones": 0,
  "traffic_disruptions": 21,
  "severity_index": "High",
  "severity_score": 60,
  "cities_monitored": 7,
  "city_breakdown": [
    {
      "city": "Mumbai",
      "temperature": 29.0,
      "humidity": 70,
      "rain_alert": false,
      "traffic_count": 1,
      "critical": false,
      "status": "Normal"
    },
    {
      "city": "Chennai",
      "temperature": 30.6,
      "humidity": 85,
      "rain_alert": true,
      "traffic_count": 5,
      "critical": false,
      "status": "Alert"
    }
  ]
}
```

---

## 6️⃣ Weather Forecast (What Your App Uses)

### Mumbai 7-Day Forecast
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=forecast_7days_simple&latitude=19.0760&longitude=72.8777"
```

### Delhi 7-Day Forecast
```bash
curl -X GET "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=forecast_7days_simple&latitude=28.6139&longitude=77.2090"
```

---

## 📊 What LIVE Data Your App is Using

### **Dashboard Page** (`/dashboard`)
```
Data Source: Weather Alerts API (7 India cities)
Updates: Every time you click "Refresh Data"
Shows: Heavy rain warnings, cyclone alerts, storm warnings
```

### **Alerts Page** (`/alerts`)
```
Data Source: Weather Alerts API (7 India cities)
Updates: Real-time from HERE
Shows: All active weather alerts for India
```

### **Maps Page** (`/maps` - Active Incidents)
```
Data Source: Weather Alerts API (7 India cities)
Updates: Real-time from HERE
Shows: Weather incidents on map
```

### **Available but Not Yet Displayed**:
```
- Traffic Incidents API (accidents, closures)
- Current Weather API (temp, wind, humidity)
- 7-Day Forecast API
```

---

## 🎯 Your Backend Endpoints (Testing)

### Get India Weather Alerts
```bash
curl -X GET "http://localhost:8000/api/weather/india-alerts" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get India Traffic Incidents
```bash
curl -X GET "http://localhost:8000/api/weather/india-traffic" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Alerts Page Data
```bash
curl -X GET "http://localhost:8000/api/alerts/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Maps Active Incidents
```bash
curl -X GET "http://localhost:8000/api/maps/active-incidents" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Current Weather (Mumbai)
```bash
curl -X GET "http://localhost:8000/api/weather/current?latitude=19.0760&longitude=72.8777" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Traffic Incidents (Mumbai)
```bash
curl -X GET "http://localhost:8000/api/weather/traffic-incidents?latitude=19.0760&longitude=72.8777&radius=50000" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 📋 Insomnia Collection Structure

Create folders in Insomnia like this:

```
📁 ResQMap - HERE API Direct
  📁 Weather Alerts
    ├── Mumbai Alerts
    ├── Delhi Alerts
    ├── Chennai Alerts
    ├── Gujarat Alerts
    ├── Kolkata Alerts
    ├── Bangalore Alerts
    └── Assam Alerts
  
  📁 Traffic Incidents
    ├── Mumbai Traffic
    ├── Delhi Traffic
    ├── Bangalore Traffic
    └── Chennai Traffic
  
  📁 Current Weather
    ├── Mumbai Weather
    ├── Delhi Weather
    └── Chennai Weather
  
  📁 Forecasts
    ├── Mumbai Forecast
    └── Delhi Forecast

📁 ResQMap - Your Backend
  📁 Weather
    ├── India Alerts (LIVE)
    ├── India Traffic (LIVE)
    ├── Current Weather
    └── Traffic Incidents
  
  📁 Alerts
    ├── Get All Alerts (LIVE)
    ├── Get Alert Summary
    └── Create Alert
  
  📁 Maps
    ├── Active Incidents (LIVE)
    └── Get Map Layers
  
  📁 Dashboard
    ├── Get Stats
    └── Recent Alerts (LIVE)
```

---

## 🔍 How to Verify Data is LIVE

### Step 1: Test HERE API Directly
```bash
# Run this in terminal
curl "https://weather.cc.api.here.com/weather/1.0/report.json?apiKey=e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA&product=alerts&latitude=19.0760&longitude=72.8777"
```

### Step 2: Test Your Backend
```bash
# In Insomnia, call:
GET http://localhost:8000/api/weather/india-alerts
```

### Step 3: Compare Responses
```
If Mumbai alert from HERE matches Mumbai alert from your backend
→ Data is LIVE! ✅
```

---

## 🌍 India Locations We're Monitoring

| City | Coordinates | Why |
|------|-------------|-----|
| **Mumbai** | 19.0760, 72.8777 | Monsoon flooding, coastal cyclones |
| **Delhi** | 28.6139, 77.2090 | Heavy rain, temperature extremes |
| **Chennai** | 13.0827, 80.2707 | Cyclones, coastal storms |
| **Gujarat Coast** | 23.0225, 70.1324 | Cyclone landfall zone |
| **Kolkata** | 22.5726, 88.3639 | Monsoon, river flooding |
| **Bangalore** | 12.9716, 77.5946 | Heavy rain, urban flooding |
| **Assam** | 26.2006, 92.9376 | River flooding, landslides |

---

## ✅ Summary

### **What's LIVE from HERE API**:
1. ✅ Weather Alerts - 7 India cities
2. ✅ Traffic Incidents - 4 major cities
3. ✅ Current Weather - Any coordinates
4. ✅ 7-Day Forecasts - Any coordinates

### **Where It's Used**:
- ✅ Dashboard → Recent Alerts section
- ✅ Alerts Page → All alerts
- ✅ Maps Page → Active Incidents
- ✅ Available via API → Traffic, Weather, Forecast endpoints

### **All cURL commands above are ready to copy into Insomnia!** 🎉

---

## 🚀 Quick Import to Insomnia

1. Open Insomnia
2. Create new collection: "ResQMap - HERE API"
3. Copy each cURL command above
4. Paste into Insomnia → It auto-creates the request!
5. Test and see LIVE data from HERE servers

**Your app is now 100% powered by LIVE HERE API data!** ✅
