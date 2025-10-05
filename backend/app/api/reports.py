from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random
import string

from app.db.database import get_db
from app.db.models import Report, User
from app.api.auth import get_current_user

router = APIRouter()


class ReportCreate(BaseModel):
    title: str
    type: str
    region: str
    data: dict


class ReportResponse(BaseModel):
    id: int
    report_id: str
    title: str
    type: str
    region: str
    status: str
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


def generate_report_id(type_prefix: str) -> str:
    """Generate unique report ID"""
    year = datetime.now().year
    random_num = ''.join(random.choices(string.digits, k=3))
    return f"RPT-{year}-{random_num}"


@router.get("/", response_model=List[ReportResponse])
async def get_reports(
    type: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports with optional filters"""
    query = db.query(Report)
    
    if type:
        query = query.filter(Report.type == type)
    if region:
        query = query.filter(Report.region == region)
    if status:
        query = query.filter(Report.status == status)
    
    reports = query.order_by(Report.created_at.desc()).all()
    return reports


@router.get("/summary")
async def get_reports_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report statistics"""
    total = db.query(Report).count()
    pending = db.query(Report).filter(Report.status == "Pending Review").count()
    completed = db.query(Report).filter(Report.status == "Completed").count()
    in_progress = db.query(Report).filter(Report.status == "In Progress").count()
    
    # This month
    from datetime import timedelta
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    this_month = db.query(Report).filter(Report.created_at >= month_start).count()
    
    return {
        "total_reports": total,
        "pending_review": pending,
        "this_month": this_month,
        "downloads": 1284,  # Mock data
        "status_breakdown": {
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending
        }
    }


@router.post("/", response_model=ReportResponse)
async def create_report(
    report: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new report"""
    report_id = generate_report_id(report.type)
    
    new_report = Report(
        report_id=report_id,
        title=report.title,
        type=report.type,
        region=report.region,
        status="In Progress",
        created_by=f"{current_user.first_name} {current_user.last_name}",
        data=report.data,
        user_id=current_user.id
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    return new_report


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report"""
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.patch("/{report_id}/status")
async def update_report_status(
    report_id: str,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update report status"""
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report.status = status
    db.commit()
    
    return {"message": f"Report status updated to {status}"}


@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export report in specified format"""
    report = db.query(Report).filter(Report.report_id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # In production, generate actual PDF/GeoTIFF
    return {
        "message": f"Report {report_id} exported as {format}",
        "download_url": f"/downloads/{report_id}.{format}"
    }
