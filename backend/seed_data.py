"""
Seed database with sample data for demo purposes
"""
from datetime import datetime, timedelta
from app.db.database import SessionLocal, engine
from app.db.models import Base, User, Alert, Report, DamagedZone, FloodedArea, DisplacedPopulation, RoadStatus
from app.api.auth import get_password_hash

def seed_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create demo user
        demo_user = User(
            email="admin@emergency",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("Admin#123"),
            organization="Emergency Management Agency",
            role="System Administrator",
            phone_number="+1 (555) 123-4567",
            timezone="Eastern (EST)",
            last_login=datetime.utcnow()
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        # Create sample alerts - India specific
        alerts = [
            Alert(
                title="Cyclone Biparjoy Approaching Gujarat Coast",
                description="Severe cyclonic storm expected to make landfall near Jakhau Port within 6 hours. Wind speeds up to 140 km/h. Immediate evacuation advised for coastal areas.",
                category="Cyclone",
                severity="Critical",
                location="Gujarat Coast",
                latitude=23.0225,
                longitude=70.1324,
                status="Active",
                action_required=True,
                affected_population=1500000,
                created_at=datetime.utcnow() - timedelta(minutes=2),
                user_id=demo_user.id
            ),
            Alert(
                title="Severe Monsoon Flooding - Mumbai Metropolitan",
                description="Heavy rainfall causing severe flooding in Mumbai and suburbs. Train services disrupted. People advised to stay indoors. Water levels rising in low-lying areas.",
                category="Flood",
                severity="High",
                location="Mumbai, Maharashtra",
                latitude=19.0760,
                longitude=72.8777,
                status="Active",
                action_required=True,
                affected_population=3200000,
                created_at=datetime.utcnow() - timedelta(minutes=15),
                user_id=demo_user.id
            ),
            Alert(
                title="Flood Alert - Brahmaputra River Rising",
                description="Water levels in Brahmaputra river rising due to heavy rainfall in upper catchment areas. Several districts in Assam on high alert.",
                category="Flood",
                severity="Medium",
                location="Assam",
                latitude=26.2006,
                longitude=92.9376,
                status="Active",
                action_required=False,
                affected_population=850000,
                created_at=datetime.utcnow() - timedelta(hours=2),
                user_id=demo_user.id
            )
        ]
        db.add_all(alerts)
        
        # Create sample reports - India specific
        reports = [
            Report(
                report_id="RPT-2025-001",
                title="Gujarat Cyclone Biparjoy Impact Assessment",
                type="Damage Assessment",
                region="Gujarat",
                status="Completed",
                created_by="NDRF Team Gujarat",
                data={"damage_level": "severe", "buildings_affected": 2850, "power_outages": 125000},
                created_at=datetime.utcnow() - timedelta(days=1),
                user_id=demo_user.id
            ),
            Report(
                report_id="RPT-2025-002",
                title="Mumbai Monsoon Flood Response",
                type="Response Summary",
                region="Mumbai, Maharashtra",
                status="In Progress",
                created_by="BMC Disaster Management",
                data={"evacuees": 85000, "relief_camps": 45, "medical_teams": 18},
                created_at=datetime.utcnow() - timedelta(hours=12),
                user_id=demo_user.id
            ),
            Report(
                report_id="RPT-2025-003",
                title="Assam Flood Monitoring Report",
                type="Operational Report",
                region="Assam",
                status="In Progress",
                created_at=datetime.utcnow() - timedelta(days=2),
                created_by="Assam SDRF",
                data={"affected_villages": 234, "rescue_operations": 67, "relief_distributed": "12 tons"},
                user_id=demo_user.id
            )
        ]
        db.add_all(reports)
        
        # Create sample damaged zones - India specific
        damaged_zones = [
            DamagedZone(
                name="Jakhau Port Area",
                latitude=23.0225,
                longitude=70.1324,
                radius=800,
                damage_level="Severe",
                infrastructure_type="Building",
                confidence_score=0.92
            ),
            DamagedZone(
                name="Mumbai Coastal Road",
                latitude=19.0760,
                longitude=72.8777,
                radius=1500,
                damage_level="Moderate",
                infrastructure_type="Road",
                confidence_score=0.85
            )
        ]
        db.add_all(damaged_zones)
        
        # Create sample flooded areas - India specific
        flooded_areas = [
            FloodedArea(
                name="Mumbai Mithi River Basin",
                latitude=19.0760,
                longitude=72.8777,
                area_sqkm=22.5,
                water_level=3.2,
                severity="High",
                confidence_score=0.88
            ),
            FloodedArea(
                name="Brahmaputra Floodplains",
                latitude=26.2006,
                longitude=92.9376,
                area_sqkm=45.8,
                water_level=2.5,
                severity="High",
                confidence_score=0.82
            )
        ]
        db.add_all(flooded_areas)
        
        # Create sample displaced populations - India specific
        displaced = [
            DisplacedPopulation(
                location="Jakhau Relief Camp",
                latitude=23.0225,
                longitude=70.1324,
                estimated_count=45000,
                displacement_type="Evacuation"
            ),
            DisplacedPopulation(
                location="Mumbai BKC Evacuation Center",
                latitude=19.0760,
                longitude=72.8777,
                estimated_count=28000,
                displacement_type="Shelter"
            ),
            DisplacedPopulation(
                location="Assam Flood Relief Camp",
                latitude=26.2006,
                longitude=92.9376,
                estimated_count=15500,
                displacement_type="Shelter"
            )
        ]
        db.add_all(displaced)
        
        # Create sample road statuses - India specific
        roads = [
            RoadStatus(
                road_name="NH 8A (Jakhau-Bhuj)",
                latitude=23.0225,
                longitude=70.1324,
                status="Closed",
                length_km=65.5,
                reason="Cyclone Damage"
            ),
            RoadStatus(
                road_name="Western Express Highway, Mumbai",
                latitude=19.0760,
                longitude=72.8777,
                status="Restricted",
                length_km=25.0,
                reason="Severe Waterlogging"
            ),
            RoadStatus(
                road_name="NH 37 Assam Sector",
                latitude=26.2006,
                longitude=92.9376,
                status="Partially Blocked",
                length_km=85.0,
                reason="Flooding"
            )
        ]
        db.add_all(roads)
        
        db.commit()
        print("Database seeded successfully!")
        print(f"Demo User - Email: admin@emergency | Password: Admin#123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
