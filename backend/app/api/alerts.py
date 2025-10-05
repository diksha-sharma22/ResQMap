from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db.models import Alert, User
from app.api.auth import get_current_user
from app.core.websocket_manager import manager

router = APIRouter()


class AlertCreate(BaseModel):
    title: str
    description: str
    category: str
    severity: str
    location: str
    latitude: float
    longitude: float
    action_required: bool = False
    affected_population: Optional[int] = None


class AlertUpdate(BaseModel):
    is_read: Optional[bool] = None
    status: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    severity: str
    location: str
    latitude: float
    longitude: float
    status: str
    is_read: bool
    action_required: bool
    affected_population: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/")
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    is_read: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get LIVE weather alerts from HERE API (not database)"""
    import httpx
    from app.core.config import settings
    
    # India locations to check for weather alerts
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
    alert_id = 1
    
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
                        
                        # Skip if severity filter doesn't match
                        if severity and mapped_severity != severity:
                            continue
                        
                        # If type is numeric, use description
                        if str(alert_type).isdigit():
                            alert_title = f"{alert_desc}" if alert_desc else f"Weather Alert - {location['name']}"
                        else:
                            alert_title = alert_type
                        
                        all_alerts.append({
                            "id": alert_id,
                            "title": alert_title,
                            "description": alert_desc if alert_desc else "Severe weather conditions expected",
                            "category": "Weather",
                            "severity": mapped_severity,
                            "location": location["name"],
                            "latitude": location["lat"],
                            "longitude": location["lon"],
                            "status": "Active",
                            "is_read": False,
                            "action_required": severity_raw.lower() in ["extreme", "severe"],
                            "affected_population": 0,
                            "created_at": datetime.utcnow().isoformat()
                        })
                        alert_id += 1
                        
                except Exception:
                    continue
        
        return all_alerts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch weather alerts: {str(e)}")


@router.get("/summary")
async def get_alerts_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get alert statistics from LIVE HERE API data"""
    # Fetch live alerts
    alerts = await get_alerts(current_user=current_user, db=db)
    
    total = len(alerts)
    unread = len([a for a in alerts if not a.get('is_read', False)])
    critical = len([a for a in alerts if a.get('severity') == "Critical"])
    action_required = len([a for a in alerts if a.get('action_required', False)])
    
    return {
        "total_alerts": total,
        "unread": unread,
        "critical": critical,
        "action_required": action_required
    }


@router.post("/", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new alert"""
    new_alert = Alert(
        **alert.dict(),
        user_id=current_user.id
    )
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    # Broadcast alert to all connected clients
    await manager.broadcast_alert({
        "id": new_alert.id,
        "title": new_alert.title,
        "severity": new_alert.severity,
        "category": new_alert.category,
        "location": new_alert.location
    })
    
    return new_alert


@router.patch("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update alert status"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    if alert_update.is_read is not None:
        alert.is_read = alert_update.is_read
    if alert_update.status is not None:
        alert.status = alert_update.status
    
    alert.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(alert)
    
    return alert


@router.post("/mark-all-read")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark all alerts as read"""
    db.query(Alert).update({"is_read": True})
    db.commit()
    return {"message": "All alerts marked as read"}


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an alert"""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}
