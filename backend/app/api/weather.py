from fastapi import APIRouter, Depends, HTTPException
import httpx
from typing import Optional

from app.core.config import settings
from app.api.auth import get_current_user, User

router = APIRouter()


@router.get("/current")
async def get_current_weather(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
):
    """Get current weather data from HERE Weather API"""
    
    if not settings.HERE_API_KEY:
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "temperature": 28,
            "conditions": "Partly Cloudy",
            "wind_speed": 15,
            "humidity": 72,
            "pressure": 1012
        }
    
    url = f"{settings.HERE_BASE_URL}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": latitude,
        "longitude": longitude,
        "product": "observation",
        "oneobservation": "true"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            observations = data.get("observations", {}).get("location", [])
            if observations:
                obs = observations[0].get("observation", [{}])[0]
                return {
                    "temperature": obs.get("temperature"),
                    "conditions": obs.get("description"),
                    "wind_speed": obs.get("windSpeed"),
                    "humidity": obs.get("humidity"),
                    "pressure": obs.get("barometerPressure"),
                    "visibility": obs.get("visibility"),
                    "comfort": obs.get("comfort")
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@router.get("/forecast")
async def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Get weather forecast from HERE Weather API"""
    
    if not settings.HERE_API_KEY:
        # Return mock data
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "forecast": [
                {"day": "Mon", "high": 30, "low": 22, "condition": "Sunny", "precipitation": 10},
                {"day": "Tue", "high": 28, "low": 21, "condition": "Cloudy", "precipitation": 40},
                {"day": "Wed", "high": 26, "low": 20, "condition": "Rainy", "precipitation": 80},
                {"day": "Thu", "high": 27, "low": 21, "condition": "Partly Cloudy", "precipitation": 30},
                {"day": "Fri", "high": 29, "low": 22, "condition": "Sunny", "precipitation": 15},
                {"day": "Sat", "high": 31, "low": 23, "condition": "Sunny", "precipitation": 5},
                {"day": "Sun", "high": 30, "low": 23, "condition": "Partly Cloudy", "precipitation": 20}
            ]
        }
    
    url = f"{settings.HERE_BASE_URL}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": latitude,
        "longitude": longitude,
        "product": "forecast_7days_simple"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@router.get("/severe-weather")
async def get_severe_weather_alerts(
    latitude: float,
    longitude: float,
    current_user: User = Depends(get_current_user)
):
    """Get severe weather alerts from HERE Weather API"""
    
    if not settings.HERE_API_KEY:
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "alerts": []
        }
    
    url = f"{settings.HERE_BASE_URL}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": latitude,
        "longitude": longitude,
        "product": "alerts"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract and format alerts
            alerts_data = data.get("alerts", {}).get("alerts", [])
            formatted_alerts = []
            
            for alert in alerts_data:
                formatted_alerts.append({
                    "type": alert.get("type", "Weather Alert"),
                    "severity": alert.get("severity", "Unknown"),
                    "description": alert.get("description", ""),
                    "valid_from": alert.get("validTimeLocal", ""),
                    "valid_until": alert.get("expireTimeLocal", ""),
                    "location": f"{latitude}, {longitude}"
                })
            
            return {
                "alerts": formatted_alerts,
                "count": len(formatted_alerts),
                "location": {"latitude": latitude, "longitude": longitude}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@router.get("/india-alerts")
async def get_india_weather_alerts(
    current_user: User = Depends(get_current_user)
):
    """Get live weather alerts for major India locations"""
    
    if not settings.HERE_API_KEY:
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "alerts": []
        }
    
    # Major India locations to check for weather alerts
    india_locations = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"name": "Gujarat Coast", "lat": 23.0225, "lon": 70.1324},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"name": "Assam", "lat": 26.2006, "lon": 92.9376},
    ]
    
    all_alerts = []
    
    try:
        async with httpx.AsyncClient() as client:
            for location in india_locations:
                url = f"{settings.HERE_BASE_URL}/report.json"
                params = {
                    "apiKey": settings.HERE_API_KEY,
                    "latitude": location["lat"],
                    "longitude": location["lon"],
                    "product": "alerts"
                }
                
                try:
                    response = await client.get(url, params=params, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    alerts_data = data.get("alerts", {}).get("alerts", [])
                    
                    for alert in alerts_data:
                        # Parse alert type properly
                        alert_type = alert.get("type", "Weather Alert")
                        alert_desc = alert.get("description", "")
                        
                        # If type is numeric, use description or create better title
                        if str(alert_type).isdigit():
                            alert_title = f"{alert_desc}" if alert_desc else f"Weather Alert - {location['name']}"
                        else:
                            alert_title = alert_type
                        
                        all_alerts.append({
                            "title": alert_title,
                            "category": alert.get("category", "Weather"),
                            "severity": map_alert_severity(alert.get("severity", "moderate")),
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "description": alert_desc if alert_desc else "Severe weather conditions expected",
                            "action_required": alert.get("severity", "").lower() in ["extreme", "severe"],
                            "valid_from": alert.get("validTimeLocal", ""),
                            "valid_until": alert.get("expireTimeLocal", ""),
                            "source": "HERE Weather API"
                        })
                except Exception as loc_error:
                    # Skip locations that fail
                    continue
        
        return {
            "alerts": all_alerts,
            "count": len(all_alerts),
            "locations_checked": len(india_locations),
            "source": "live"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


def map_alert_severity(severity: str) -> str:
    """Map HERE severity levels to our severity levels"""
    severity_lower = severity.lower()
    if severity_lower in ["extreme", "severe"]:
        return "Critical"
    elif severity_lower in ["moderate", "minor"]:
        return "High"
    else:
        return "Medium"


@router.get("/traffic-incidents")
async def get_traffic_incidents(
    latitude: float,
    longitude: float,
    radius: int = 50000,  # 50km radius in meters
    current_user: User = Depends(get_current_user)
):
    """Get live traffic incidents from HERE Traffic API
    
    Includes: accidents, road closures, construction, traffic jams
    """
    
    if not settings.HERE_API_KEY:
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "incidents": []
        }
    
    # HERE Traffic API v7 endpoint
    url = "https://data.traffic.hereapi.com/v7/incidents"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "in": f"circle:{latitude},{longitude};r={radius}",
        "locationReferencing": "none"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            incidents = []
            for item in data.get("results", []):
                incident = item.get("incident", {})
                location = item.get("location", {})
                geo = location.get("shape", {}).get("links", [{}])[0].get("points", [{}])[0] if location.get("shape", {}).get("links") else {}
                
                # Extract incident type and description
                incident_type = incident.get("type", {}).get("description", "Traffic Incident")
                description = incident.get("description", {}).get("value", "Traffic disruption")
                
                incidents.append({
                    "id": item.get("incidentId", "unknown"),
                    "type": incident_type,
                    "description": description,
                    "severity": map_incident_severity(incident.get("criticality", {}).get("description", "minor")),
                    "start_time": incident.get("startTime", ""),
                    "end_time": incident.get("endTime", ""),
                    "latitude": geo.get("lat", latitude),
                    "longitude": geo.get("lng", longitude),
                    "verified": incident.get("verified", False)
                })
            
            return {
                "incidents": incidents,
                "count": len(incidents),
                "radius_km": radius / 1000,
                "center": {"latitude": latitude, "longitude": longitude}
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Traffic API error: {str(e)}")


@router.get("/india-traffic")
async def get_india_traffic_incidents(
    current_user: User = Depends(get_current_user)
):
    """Get live traffic incidents for major India cities"""
    
    if not settings.HERE_API_KEY:
        return {
            "message": "HERE API Key not configured",
            "mock_data": True,
            "incidents": []
        }
    
    # Major India locations
    india_locations = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    ]
    
    all_incidents = []
    
    try:
        async with httpx.AsyncClient() as client:
            for location in india_locations:
                url = "https://data.traffic.hereapi.com/v7/incidents"
                params = {
                    "apiKey": settings.HERE_API_KEY,
                    "in": f"circle:{location['lat']},{location['lon']};r=30000",  # 30km radius
                    "locationReferencing": "none"
                }
                
                try:
                    response = await client.get(url, params=params, timeout=10.0)
                    response.raise_for_status()
                    data = response.json()
                    
                    for item in data.get("results", [])[:5]:  # Limit to 5 per city
                        incident_details = item.get("incidentDetails", {})
                        
                        # Extract type and description correctly
                        type_desc = incident_details.get("typeDescription", {})
                        incident_type = type_desc.get("value", "Traffic Incident") if type_desc else "Traffic Incident"
                        
                        desc_obj = incident_details.get("description", {})
                        description = desc_obj.get("value", "Traffic disruption") if desc_obj else "Traffic disruption"
                        
                        # Extract criticality
                        criticality = incident_details.get("criticality", "minor")
                        
                        all_incidents.append({
                            "id": incident_details.get("id", "unknown"),
                            "type": incident_type,
                            "description": description,
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "severity": map_incident_severity(criticality),
                            "start_time": incident_details.get("startTime", ""),
                            "verified": incident_details.get("roadClosed", False)
                        })
                except Exception:
                    continue
        
        return {
            "incidents": all_incidents,
            "count": len(all_incidents),
            "cities_checked": len(india_locations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Traffic API error: {str(e)}")


@router.get("/impact-analysis")
async def get_weather_impact_analysis(
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive weather impact analysis from HERE API"""
    
    if not settings.HERE_API_KEY:
        return {"error": "HERE API Key not configured"}
    
    india_locations = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    ]
    
    temperatures = []
    humidities = []
    rain_alerts = 0
    critical_zones = 0
    traffic_disruptions = 0
    city_data = []  # Store per-city data
    
    try:
        async with httpx.AsyncClient() as client:
            for location in india_locations:
                city_info = {
                    "city": location["name"],
                    "temperature": None,
                    "humidity": None,
                    "windspeed": None,
                    "rain_alert": False,
                    "traffic_count": 0,
                    "traffic_incidents": [],  # Store actual incident details
                    "critical": False,
                    "status": "Normal"
                }
                # Get weather alerts
                try:
                    alerts_url = f"{settings.HERE_BASE_URL}/report.json"
                    alerts_params = {
                        "apiKey": settings.HERE_API_KEY,
                        "latitude": location["lat"],
                        "longitude": location["lon"],
                        "product": "alerts"
                    }
                    alerts_response = await client.get(alerts_url, params=alerts_params, timeout=10.0)
                    alerts_data = alerts_response.json()
                    alerts_list = alerts_data.get("alerts", {}).get("alerts", [])
                    
                    if alerts_list:
                        rain_alerts += 1
                        city_info["rain_alert"] = True
                        for alert in alerts_list:
                            if alert.get("severity", "").lower() in ["extreme", "severe"]:
                                critical_zones += 1
                                city_info["critical"] = True
                                city_info["status"] = "Critical"
                                break
                        if not city_info["critical"]:
                            city_info["status"] = "Alert"
                except Exception:
                    pass
                
                # Get current weather
                try:
                    weather_url = f"{settings.HERE_BASE_URL}/report.json"
                    weather_params = {
                        "apiKey": settings.HERE_API_KEY,
                        "latitude": location["lat"],
                        "longitude": location["lon"],
                        "product": "observation",
                        "oneobservation": "true"
                    }
                    weather_response = await client.get(weather_url, params=weather_params, timeout=10.0)
                    weather_data = weather_response.json()
                    obs = weather_data.get("observations", {}).get("location", [{}])[0].get("observation", [{}])[0]
                    
                    if obs.get("temperature"):
                        temp = float(obs["temperature"])
                        temperatures.append(temp)
                        city_info["temperature"] = round(temp, 1)
                    if obs.get("humidity"):
                        hum = float(obs["humidity"])
                        humidities.append(hum)
                        city_info["humidity"] = round(hum, 1)
                    if obs.get("windSpeed"):
                        wind = float(obs["windSpeed"])
                        city_info["windspeed"] = round(wind, 1)
                except Exception:
                    pass
                
                # Get traffic incidents
                try:
                    traffic_url = "https://data.traffic.hereapi.com/v7/incidents"
                    traffic_params = {
                        "apiKey": settings.HERE_API_KEY,
                        "in": f"circle:{location['lat']},{location['lon']};r=30000",
                        "locationReferencing": "none"
                    }
                    traffic_response = await client.get(traffic_url, params=traffic_params, timeout=10.0)
                    traffic_data = traffic_response.json()
                    incidents = traffic_data.get("results", [])
                    
                    city_traffic = 0
                    for incident in incidents[:10]:  # Check more incidents
                        incident_details = incident.get("incidentDetails", {})
                        if incident_details.get("roadClosed") or incident_details.get("criticality") == "critical":
                            traffic_disruptions += 1
                            city_traffic += 1
                            
                            # Extract incident details
                            type_desc = incident_details.get("typeDescription", {})
                            incident_type = type_desc.get("value", "Traffic Incident") if type_desc else "Traffic Incident"
                            
                            desc_obj = incident_details.get("description", {})
                            description = desc_obj.get("value", "Road disruption") if desc_obj else "Road disruption"
                            
                            # Store incident details
                            city_info["traffic_incidents"].append({
                                "type": incident_type,
                                "description": description,
                                "road_closed": incident_details.get("roadClosed", False),
                                "criticality": incident_details.get("criticality", "unknown"),
                                "start_time": incident_details.get("startTime", "")
                            })
                    
                    city_info["traffic_count"] = city_traffic
                    if city_traffic >= 3 and city_info["status"] == "Normal":
                        city_info["status"] = "Warning"
                except Exception:
                    pass
                
                city_data.append(city_info)
        
        # Calculate metrics
        avg_temp = sum(temperatures) / len(temperatures) if temperatures else 0
        min_temp = min(temperatures) if temperatures else 0
        max_temp = max(temperatures) if temperatures else 0
        avg_humidity = sum(humidities) / len(humidities) if humidities else 0
        
        # Calculate severity index
        severity_score = 0
        if critical_zones > 0:
            severity_score += 40
        if rain_alerts >= 3:
            severity_score += 30
        if traffic_disruptions >= 5:
            severity_score += 20
        if avg_humidity > 70:
            severity_score += 10
        
        severity_level = "Low"
        if severity_score >= 70:
            severity_level = "Critical"
        elif severity_score >= 50:
            severity_level = "High"
        elif severity_score >= 30:
            severity_level = "Medium"
        
        return {
            "temperature_range": {
                "min": round(min_temp, 1),
                "max": round(max_temp, 1),
                "avg": round(avg_temp, 1)
            },
            "humidity": round(avg_humidity, 1),
            "rain_alerts": rain_alerts,
            "critical_zones": critical_zones,
            "traffic_disruptions": traffic_disruptions,
            "severity_index": severity_level,
            "severity_score": severity_score,
            "cities_monitored": len(india_locations),
            "city_breakdown": city_data,  # NEW: Per-city data
            "data_source": "LIVE - HERE Weather & Traffic API"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact analysis error: {str(e)}")


def map_incident_severity(criticality: str) -> str:
    """Map traffic incident criticality to severity levels"""
    crit_lower = criticality.lower()
    if "critical" in crit_lower or "major" in crit_lower:
        return "Critical"
    elif "minor" in crit_lower:
        return "Medium"
    else:
        return "High"
