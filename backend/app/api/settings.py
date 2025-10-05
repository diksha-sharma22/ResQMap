from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.db.database import get_db
from app.db.models import User
from app.api.auth import get_current_user, get_password_hash

router = APIRouter()


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    organization: Optional[str] = None
    role: Optional[str] = None
    phone_number: Optional[str] = None
    timezone: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/profile")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user profile"""
    return {
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "organization": current_user.organization,
        "role": current_user.role,
        "phone_number": current_user.phone_number,
        "timezone": current_user.timezone,
        "account_status": {
            "account_type": "Premium",
            "security_level": "Level 3",
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
            "member_since": current_user.created_at.strftime("%b %Y")
        }
    }


@router.patch("/profile")
async def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = db.query(User).filter(User.id == current_user.id).first()
    
    update_data = profile_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Profile updated successfully"}


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    from app.api.auth import verify_password
    
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not verify_password(password_change.current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    user.hashed_password = get_password_hash(password_change.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/notification-preferences")
async def get_notification_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences"""
    return {
        "severity_levels": {
            "critical": True,
            "high": True,
            "medium": False,
            "low": False
        },
        "delivery_methods": {
            "email": True,
            "sms": True,
            "push_notifications": True
        }
    }


@router.patch("/notification-preferences")
async def update_notification_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    # In production, store in database
    return {"message": "Notification preferences updated"}
