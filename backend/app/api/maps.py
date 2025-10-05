from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.db.database import get_db
from app.db.models import DamagedZone, FloodedArea, DisplacedPopulation, RoadStatus, User, Alert
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/layers")
async def get_map_layers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all map layer data"""
    
    # Damaged zones
    damaged_zones = db.query(DamagedZone).all()
    damaged_data = [{
        "id": zone.id,
        "name": zone.name,
        "latitude": zone.latitude,
        "longitude": zone.longitude,
        "radius": zone.radius,
        "damage_level": zone.damage_level,
        "infrastructure_type": zone.infrastructure_type,
        "confidence_score": zone.confidence_score,
        "detected_at": zone.detected_at.isoformat()
    } for zone in damaged_zones]
    
    # Flooded areas
    flooded_areas = db.query(FloodedArea).all()
    flooded_data = [{
        "id": area.id,
        "name": area.name,
        "latitude": area.latitude,
        "longitude": area.longitude,
        "area_sqkm": area.area_sqkm,
        "water_level": area.water_level,
        "severity": area.severity,
        "confidence_score": area.confidence_score,
        "detected_at": area.detected_at.isoformat()
    } for area in flooded_areas]
    
    # Displaced population
    displaced = db.query(DisplacedPopulation).all()
    displaced_data = [{
        "id": pop.id,
        "location": pop.location,
        "latitude": pop.latitude,
        "longitude": pop.longitude,
        "estimated_count": pop.estimated_count,
        "displacement_type": pop.displacement_type,
        "last_updated": pop.last_updated.isoformat()
    } for pop in displaced]
    
    # Road status
    roads = db.query(RoadStatus).all()
    road_data = [{
        "id": road.id,
        "road_name": road.road_name,
        "latitude": road.latitude,
        "longitude": road.longitude,
        "status": road.status,
        "length_km": road.length_km,
        "reason": road.reason,
        "updated_at": road.updated_at.isoformat()
    } for road in roads]
    
    return {
        "damaged_zones": {
            "count": len(damaged_data),
            "data": damaged_data
        },
        "flooded_areas": {
            "count": len(flooded_data),
            "data": flooded_data
        },
        "displaced_population": {
            "total_count": sum([p["estimated_count"] for p in displaced_data]),
            "locations": len(displaced_data),
            "data": displaced_data
        },
        "road_status": {
            "total_km": sum([r["length_km"] for r in road_data]),
            "data": road_data
        }
    }


@router.get("/active-incidents")
async def get_active_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LIVE weather incidents from HERE API (not database)"""
    import httpx
    from app.core.config import settings
    
    # India locations to check
    india_locations = [
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
        {"name": "Gujarat Coast", "lat": 23.0225, "lon": 70.1324},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
        {"name": "Assam", "lat": 26.2006, "lon": 92.9376},
    ]
    
    incidents = []
    incident_id = 1
    
    if not settings.HERE_API_KEY:
        return []
    
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
                        alert_type = alert.get("type", "Weather Alert")
                        alert_desc = alert.get("description", "")
                        severity_raw = alert.get("severity", "moderate")
                        
                        # Map severity
                        if severity_raw.lower() in ["extreme", "severe"]:
                            mapped_severity = "Critical"
                        elif severity_raw.lower() in ["moderate"]:
                            mapped_severity = "High"
                        else:
                            mapped_severity = "Medium"
                        
                        # If type is numeric, use description
                        if str(alert_type).isdigit():
                            alert_title = f"{alert_desc}" if alert_desc else f"Weather Alert"
                        else:
                            alert_title = alert_type
                        
                        incidents.append({
                            "id": f"live-{incident_id}",
                            "name": alert_title,
                            "type": "Weather",
                            "severity": mapped_severity,
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "affected_population": 0  # HERE API doesn't provide this
                        })
                        incident_id += 1
                        
                except Exception:
                    continue
        
        return incidents
        
    except Exception:
        return []


@router.get("/time-evolution")
async def get_time_evolution(
    incident_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get time evolution data for a specific incident"""
    # Mock data for demonstration
    return {
        "incident_id": incident_id,
        "start_date": "2025-09-26",
        "current_date": "2025-10-05",
        "progress_percentage": 75,
        "timeline": [
            {"date": "2025-09-26", "severity": 20, "affected": 500000},
            {"date": "2025-09-28", "severity": 45, "affected": 1200000},
            {"date": "2025-09-30", "severity": 75, "affected": 1800000},
            {"date": "2025-10-02", "severity": 65, "affected": 2100000},
            {"date": "2025-10-05", "severity": 55, "affected": 1900000}
        ]
    }
