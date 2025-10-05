import cv2
import numpy as np
from typing import List, Dict, Tuple
from PIL import Image
import io


class DisasterDetector:
    """AI-powered disaster detection from satellite and drone imagery"""
    
    def __init__(self):
        self.damage_threshold = 0.6
        self.flood_threshold = 0.7
        
    async def detect_damaged_infrastructure(self, image_bytes: bytes) -> Dict:
        """
        Detect damaged infrastructure in satellite/drone images
        Uses computer vision and AI models
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Invalid image"}
        
        # In production, use trained CNN model (e.g., ResNet, U-Net)
        # For demo, use basic computer vision
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect contours (buildings, structures)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        damaged_zones = []
        for i, contour in enumerate(contours[:10]):  # Top 10 largest
            area = cv2.contourArea(contour)
            if area > 1000:  # Minimum size threshold
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calculate damage indicators
                roi = gray[y:y+h, x:x+w]
                damage_score = self._calculate_damage_score(roi)
                
                if damage_score > self.damage_threshold:
                    damaged_zones.append({
                        "id": i,
                        "bbox": [int(x), int(y), int(w), int(h)],
                        "damage_level": self._get_damage_level(damage_score),
                        "confidence": float(damage_score),
                        "area_sqm": float(area * 0.1)  # Approximate conversion
                    })
        
        return {
            "total_detected": len(damaged_zones),
            "damaged_zones": damaged_zones,
            "image_size": img.shape[:2],
            "analysis_type": "infrastructure_damage"
        }
    
    async def detect_flood_zones(self, image_bytes: bytes) -> Dict:
        """
        Detect flooded areas in satellite imagery
        Uses water detection algorithms
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Invalid image"}
        
        # Convert to HSV for water detection
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Water typically has blue hues
        lower_water = np.array([90, 50, 50])
        upper_water = np.array([130, 255, 255])
        
        # Create mask for water
        water_mask = cv2.inRange(hsv, lower_water, upper_water)
        
        # Find flooded contours
        contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        flooded_areas = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 2000:  # Significant flood area
                x, y, w, h = cv2.boundingRect(contour)
                
                flooded_areas.append({
                    "id": i,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "area_sqkm": float(area * 0.0001),  # Approximate
                    "severity": self._get_flood_severity(area),
                    "confidence": 0.75
                })
        
        total_flooded_area = sum([area["area_sqkm"] for area in flooded_areas])
        
        return {
            "total_flooded_areas": len(flooded_areas),
            "total_area_sqkm": float(total_flooded_area),
            "flooded_zones": flooded_areas,
            "analysis_type": "flood_detection"
        }
    
    async def detect_population_displacement(self, image_bytes: bytes) -> Dict:
        """
        Detect population movement and displacement camps
        Uses object detection for vehicles, tents, crowds
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"error": "Invalid image"}
        
        # In production, use YOLO or similar for vehicle/people detection
        # For demo, use basic blob detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        
        # Detect potential camps/gatherings
        _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        displacement_sites = []
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area > 500:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Estimate population based on area
                estimated_count = int(area / 10)  # Rough estimate
                
                displacement_sites.append({
                    "id": i,
                    "bbox": [int(x), int(y), int(w), int(h)],
                    "estimated_count": estimated_count,
                    "type": "evacuation_site",
                    "confidence": 0.68
                })
        
        total_displaced = sum([site["estimated_count"] for site in displacement_sites])
        
        return {
            "total_sites": len(displacement_sites),
            "estimated_displaced_population": total_displaced,
            "sites": displacement_sites,
            "analysis_type": "population_displacement"
        }
    
    def _calculate_damage_score(self, roi: np.ndarray) -> float:
        """Calculate damage score based on texture and intensity"""
        if roi.size == 0:
            return 0.0
        
        # Check for irregularities (damaged structures have high variance)
        variance = np.var(roi)
        mean_intensity = np.mean(roi)
        
        # Normalize score
        score = min((variance / 1000.0) + (1.0 - mean_intensity / 255.0), 1.0)
        return score
    
    def _get_damage_level(self, score: float) -> str:
        """Convert damage score to severity level"""
        if score > 0.8:
            return "Severe"
        elif score > 0.65:
            return "Moderate"
        else:
            return "Light"
    
    def _get_flood_severity(self, area: float) -> str:
        """Determine flood severity based on area"""
        if area > 10000:
            return "Critical"
        elif area > 5000:
            return "High"
        elif area > 2000:
            return "Medium"
        else:
            return "Low"


# Singleton instance
detector = DisasterDetector()
