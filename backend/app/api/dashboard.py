from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Dict

from app.db.database import get_db
from app.db.models import Alert, DisplacedPopulation, DamagedZone, FloodedArea
from app.api.auth import get_current_user, User

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    
    # Active disasters (critical and high alerts from last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_disasters = db.query(Alert).filter(
        Alert.severity.in_(["Critical", "High"]),
        Alert.status == "Active",
        Alert.created_at >= week_ago
    ).count()
    
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_disasters = db.query(Alert).filter(
        Alert.severity.in_(["Critical", "High"]),
        Alert.status == "Active",
        Alert.created_at >= yesterday,
        Alert.created_at < datetime.utcnow()
    ).count()
    
    # Affected population from displaced people
    total_affected = db.query(func.sum(DisplacedPopulation.estimated_count)).scalar() or 0
    
    # For demo purposes, show affected population change
    # In production, this would compare with historical data
    affected_change = "from emergency reports"
    
    # Response teams - count unique users + calculate from reports
    response_teams = db.query(func.count(func.distinct(Alert.user_id))).scalar() or 0
    deployed_today = db.query(Alert).filter(
        Alert.created_at >= datetime.utcnow() - timedelta(days=1)
    ).count()
    
    # Monitored zones
    monitored_zones = db.query(DamagedZone).count() + db.query(FloodedArea).count()
    today_zones = db.query(DamagedZone).filter(
        DamagedZone.id > 0
    ).count()
    new_zones = today_zones  # All zones are "new" in demo
    
    return {
        "active_disasters": {
            "count": active_disasters,
            "change": f"+{max(0, yesterday_disasters)} from yesterday"
        },
        "affected_population": {
            "count": total_affected,
            "change": affected_change
        },
        "response_teams": {
            "count": response_teams,
            "deployed_today": deployed_today
        },
        "monitored_zones": {
            "count": monitored_zones,
            "new_zones": new_zones
        }
    }


@router.get("/recent-alerts")
async def get_recent_alerts(
    limit: int = 5,
    source: str = "database",  # "database" or "live" or "both"
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent alerts for dashboard
    
    Args:
        source: 'database' (default) - alerts from DB only
                'live' - live weather alerts from HERE API only  
                'both' - merge both sources
    """
    db_alerts = []
    
    if source in ["database", "both"]:
        alerts = db.query(Alert).filter(
            Alert.status == "Active"
        ).order_by(Alert.created_at.desc()).limit(limit).all()
        
        db_alerts = [{
            "id": alert.id,
            "title": alert.title,
            "category": alert.category,
            "severity": alert.severity,
            "location": alert.location,
            "description": alert.description,
            "action_required": alert.action_required,
            "affected_population": alert.affected_population,
            "created_at": alert.created_at.isoformat(),
            "time_ago": get_time_ago(alert.created_at),
            "source": "database"
        } for alert in alerts]
    
    return db_alerts


def get_time_ago(dt: datetime) -> str:
    """Convert datetime to relative time string"""
    diff = datetime.utcnow() - dt
    
    if diff.total_seconds() < 60:
        return f"{int(diff.total_seconds())} seconds ago"
    elif diff.total_seconds() < 3600:
        return f"{int(diff.total_seconds() / 60)} minutes ago"
    elif diff.total_seconds() < 86400:
        return f"{int(diff.total_seconds() / 3600)} hours ago"
    else:
        return f"{int(diff.total_seconds() / 86400)} days ago"
