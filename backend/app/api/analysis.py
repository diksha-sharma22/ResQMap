from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from typing import Optional
from app.services.ai_detector import detector
from app.api.auth import get_current_user, User

router = APIRouter()


@router.post("/analyze/damage")
async def analyze_damage(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze satellite/drone imagery for damaged infrastructure
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    try:
        result = await detector.detect_damaged_infrastructure(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/flood")
async def analyze_flood(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze satellite imagery for flooded zones
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    try:
        result = await detector.detect_flood_zones(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/displacement")
async def analyze_displacement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze imagery for population displacement indicators
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    try:
        result = await detector.detect_population_displacement(image_bytes)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/comprehensive")
async def comprehensive_analysis(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Run all analysis types on an image
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    image_bytes = await file.read()
    
    try:
        damage_result = await detector.detect_damaged_infrastructure(image_bytes)
        flood_result = await detector.detect_flood_zones(image_bytes)
        displacement_result = await detector.detect_population_displacement(image_bytes)
        
        return {
            "damage_analysis": damage_result,
            "flood_analysis": flood_result,
            "displacement_analysis": displacement_result,
            "summary": {
                "total_damaged_zones": damage_result.get("total_detected", 0),
                "total_flooded_areas": flood_result.get("total_flooded_areas", 0),
                "estimated_displaced": displacement_result.get("estimated_displaced_population", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
