from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    organization = Column(String)
    role = Column(String, default="Emergency Coordinator")
    phone_number = Column(String)
    timezone = Column(String, default="Eastern (EST)")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    alerts = relationship("Alert", back_populates="user")
    reports = relationship("Report", back_populates="user")


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    category = Column(String)  # Hurricane, Flood, Wildfire, etc.
    severity = Column(String)  # Critical, High, Medium, Low
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String, default="Active")  # Active, Resolved, Archived
    is_read = Column(Boolean, default=False)
    action_required = Column(Boolean, default=False)
    affected_population = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="alerts")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True)
    title = Column(String)
    type = Column(String)  # Damage Assessment, Response Summary, Operational Report
    region = Column(String)
    status = Column(String)  # Completed, In Progress, Pending Review
    created_by = Column(String)
    data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="reports")


class DamagedZone(Base):
    __tablename__ = "damaged_zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    radius = Column(Float)  # in meters
    damage_level = Column(String)  # Severe, Moderate, Light
    infrastructure_type = Column(String)  # Building, Road, Bridge, etc.
    detected_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    source = Column(String)  # Satellite, Drone, Manual


class FloodedArea(Base):
    __tablename__ = "flooded_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    area_sqkm = Column(Float)
    water_level = Column(Float)  # in meters
    severity = Column(String)  # Critical, High, Medium, Low
    detected_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)


class DisplacedPopulation(Base):
    __tablename__ = "displaced_populations"
    
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    estimated_count = Column(Integer)
    displacement_type = Column(String)  # Evacuation, Shelter, Transit
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RoadStatus(Base):
    __tablename__ = "road_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    road_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(String)  # Open, Closed, Restricted
    length_km = Column(Float)
    reason = Column(String)  # Flooding, Damage, Blocked
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
