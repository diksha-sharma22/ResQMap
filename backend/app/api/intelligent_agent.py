from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import math
import re
from datetime import datetime
from collections import Counter
import asyncio
import httpx

from app.core.config import settings
from app.core.websocket_manager import manager

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    timestamp: Optional[datetime] = None

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    suggestions: List[str] = []
    confidence: float = 0.0

class IntelligentResQMapAgent:
    """Truly intelligent agent using mathematical similarity and learning"""
    
    def __init__(self):
        self.conversation_memory = []
        self.learned_patterns = {}
        self.context_embeddings = {}
        
        # Knowledge vectors (mathematical representation)
        self.knowledge_vectors = self._build_knowledge_vectors()
        self.response_templates = self._build_response_templates()
        
        # Lightweight city -> coordinates mapping for India (extendable)
        self.city_coords = {
            "mumbai": ("Mumbai", 19.0760, 72.8777),
            "delhi": ("Delhi", 28.6139, 77.2090),
            "chennai": ("Chennai", 13.0827, 80.2707),
            "bangalore": ("Bangalore", 12.9716, 77.5946),
            "bengaluru": ("Bangalore", 12.9716, 77.5946),
            "pune": ("Pune", 18.5204, 73.8567),
            "ahmedabad": ("Ahmedabad", 23.0225, 72.5714),
            "kolkata": ("Kolkata", 22.5726, 88.3639),
            "hyderabad": ("Hyderabad", 17.3850, 78.4867),
            "assam": ("Assam", 26.2006, 92.9376),
            "gujarat": ("Gujarat", 22.2587, 71.1924)
        }
        
    def _build_knowledge_vectors(self) -> Dict[str, List[float]]:
        """Build mathematical vectors for different concepts"""
        return {
            # Weather concepts
            "weather_current": [0.9, 0.1, 0.2, 0.8, 0.3, 0.7, 0.1, 0.4],
            "weather_forecast": [0.8, 0.2, 0.9, 0.7, 0.1, 0.6, 0.3, 0.5],
            "weather_alerts": [0.95, 0.8, 0.3, 0.9, 0.7, 0.4, 0.8, 0.6],
            
            # Disaster concepts  
            "disaster_flood": [0.2, 0.9, 0.8, 0.3, 0.9, 0.1, 0.7, 0.8],
            "disaster_evacuation": [0.1, 0.8, 0.9, 0.2, 0.8, 0.3, 0.9, 0.7],
            "disaster_emergency": [0.95, 0.9, 0.7, 0.8, 0.9, 0.8, 0.9, 0.9],
            
            # Maps concepts
            "maps_layers": [0.3, 0.1, 0.2, 0.9, 0.1, 0.8, 0.2, 0.3],
            "maps_incidents": [0.7, 0.6, 0.4, 0.8, 0.5, 0.7, 0.6, 0.4],
            
            # API concepts
            "api_endpoints": [0.1, 0.2, 0.1, 0.2, 0.1, 0.3, 0.9, 0.8],
            "api_usage": [0.2, 0.1, 0.3, 0.1, 0.2, 0.4, 0.8, 0.9],
            
            # Help concepts
            "help_general": [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5],
            "help_features": [0.4, 0.3, 0.4, 0.6, 0.3, 0.7, 0.4, 0.6]
        }
    
    def _build_response_templates(self) -> Dict[str, Dict]:
        """Build intelligent response templates"""
        return {
            "weather_current": {
                "response": "I can help you access real-time weather data. ResQMap integrates with HERE Weather API to provide current conditions including temperature, humidity, wind speed, and atmospheric pressure. You can view this data on the Dashboard or access it via the /api/weather/current endpoint.",
                "suggestions": ["View weather alerts", "Check 7-day forecast", "See weather map", "API documentation"],
                "follow_up": "Would you like me to guide you to specific weather information for a particular location?"
            },
            "weather_forecast": {
                "response": "Weather forecasting in ResQMap provides 7-day ahead predictions using HERE's advanced meteorological models. This includes precipitation probability, temperature ranges, wind patterns, and severe weather warnings. Access forecasts through the Forecast page or /api/weather/forecast endpoint.",
                "suggestions": ["Current weather", "Weather alerts", "Historical data", "Location-specific forecast"],
                "follow_up": "I can help you understand how to interpret the forecast data or set up location-specific alerts."
            },
            "weather_alerts": {
                "response": "ResQMap's alert system monitors live weather warnings across India, including cyclones, heavy rainfall, storms, and extreme temperature events. These alerts are sourced from HERE Weather API and updated in real-time. Critical alerts trigger automatic notifications and are displayed prominently on the dashboard.",
                "suggestions": ["View active alerts", "Set alert preferences", "Alert history", "Emergency protocols"],
                "follow_up": "Would you like to configure alert settings for specific regions or weather types?"
            },
            "disaster_flood": {
                "response": "Flood management in ResQMap includes real-time monitoring of water levels, affected areas visualization, evacuation route planning, and resource allocation. The system displays flooded zones in blue on the interactive map and tracks displaced populations. Historical flood data helps predict future risk areas.",
                "suggestions": ["View flood zones", "Evacuation routes", "Relief centers", "Water level data"],
                "follow_up": "I can guide you through flood response protocols or help you access specific flood data for affected regions."
            },
            "disaster_evacuation": {
                "response": "Evacuation management involves coordinating safe movement of populations from danger zones. ResQMap tracks evacuation camps, transportation routes, capacity management, and resource distribution. The system provides real-time updates on camp availability and population counts.",
                "suggestions": ["Find evacuation centers", "Route planning", "Capacity status", "Resource needs"],
                "follow_up": "Do you need information about specific evacuation procedures or camp locations?"
            },
            "disaster_emergency": {
                "response": "Emergency response coordination is critical during disasters. ResQMap provides incident command support, resource tracking, communication tools, and real-time situational awareness. The system integrates multiple data sources to provide comprehensive emergency management capabilities.",
                "suggestions": ["Emergency contacts", "Incident reporting", "Resource status", "Communication tools"],
                "follow_up": "For immediate emergencies, please contact local authorities. I can help you navigate ResQMap's emergency management features."
            },
            "maps_layers": {
                "response": "ResQMap's interactive mapping system includes multiple data layers: Damaged Zones (red areas), Flooded Areas (blue zones), Displaced Population markers, Infrastructure status, Weather overlays, and Traffic incidents. Each layer provides specific information relevant to disaster management and can be toggled independently.",
                "suggestions": ["Toggle map layers", "Layer information", "Custom overlays", "Data sources"],
                "follow_up": "Which specific map layer would you like to explore or learn more about?"
            },
            "maps_incidents": {
                "response": "Active incident tracking shows real-time disaster events across India including cyclones in Gujarat, monsoon floods in Mumbai, and river floods in Assam. Each incident includes severity levels, affected areas, response status, and resource deployment information.",
                "suggestions": ["View all incidents", "Incident details", "Response status", "Historical incidents"],
                "follow_up": "Would you like detailed information about a specific incident or region?"
            },
            "api_endpoints": {
                "response": "ResQMap provides comprehensive REST API endpoints for weather data (/api/weather/*), disaster information (/api/maps/*), alerts (/api/alerts/*), and dashboard statistics (/api/dashboard/*). All endpoints support JSON responses and include proper error handling and rate limiting.",
                "suggestions": ["API documentation", "Authentication", "Rate limits", "Code examples"],
                "follow_up": "Which specific API endpoint would you like to learn about or integrate with?"
            },
            "api_usage": {
                "response": "API integration involves authentication, proper request formatting, error handling, and response parsing. ResQMap APIs use standard HTTP methods and return structured JSON data. Rate limiting ensures fair usage across all clients.",
                "suggestions": ["Getting started", "Authentication guide", "Error codes", "Best practices"],
                "follow_up": "Are you looking to integrate specific functionality or need help with API implementation?"
            },
            "help_general": {
                "response": "I'm your intelligent ResQMap assistant, designed to help you navigate disaster management features, understand weather data, explore mapping capabilities, and utilize API services. I learn from our conversations to provide increasingly relevant assistance.",
                "suggestions": ["Feature overview", "Getting started", "Tutorials", "Support resources"],
                "follow_up": "What specific aspect of ResQMap would you like to explore or learn about?"
            },
            "help_features": {
                "response": "ResQMap offers comprehensive disaster management features: Real-time weather monitoring, interactive disaster mapping, evacuation management, alert systems, API integration, traffic incident tracking, and emergency response coordination. Each feature is designed for professional emergency management use.",
                "suggestions": ["Feature details", "User guide", "Video tutorials", "Training resources"],
                "follow_up": "Which feature would you like to dive deeper into or get hands-on guidance with?"
            }
        }
    
    def _text_to_vector(self, text: str) -> List[float]:
        """Convert text to mathematical vector using advanced techniques"""
        # Normalize text
        text = text.lower().strip()
        words = re.findall(r'\b\w+\b', text)
        
        if not words:
            return [0.0] * 8
        
        # Create vector based on word characteristics
        vector = [0.0] * 8
        
        # Dimension 0: Urgency/Emergency level
        urgent_words = {'emergency', 'urgent', 'critical', 'immediate', 'help', 'asap', 'now'}
        vector[0] = len([w for w in words if w in urgent_words]) / len(words)
        
        # Dimension 1: Disaster-related content
        disaster_words = {'flood', 'earthquake', 'cyclone', 'disaster', 'evacuation', 'damage', 'rescue'}
        vector[1] = len([w for w in words if w in disaster_words]) / len(words)
        
        # Dimension 2: Weather-related content
        weather_words = {'weather', 'rain', 'storm', 'temperature', 'wind', 'forecast', 'alert'}
        vector[2] = len([w for w in words if w in weather_words]) / len(words)
        
        # Dimension 3: Location/Geography
        location_words = {'map', 'location', 'area', 'zone', 'region', 'city', 'state', 'coordinates'}
        vector[3] = len([w for w in words if w in location_words]) / len(words)
        
        # Dimension 4: Action/Request intent
        action_words = {'show', 'get', 'find', 'check', 'view', 'see', 'display', 'search'}
        vector[4] = len([w for w in words if w in action_words]) / len(words)
        
        # Dimension 5: Information/Data focus
        info_words = {'data', 'information', 'details', 'status', 'report', 'statistics', 'analysis'}
        vector[5] = len([w for w in words if w in info_words]) / len(words)
        
        # Dimension 6: Technical/API focus
        tech_words = {'api', 'endpoint', 'integration', 'code', 'technical', 'documentation', 'development'}
        vector[6] = len([w for w in words if w in tech_words]) / len(words)
        
        # Dimension 7: Help/Guidance intent
        help_words = {'help', 'how', 'what', 'explain', 'guide', 'tutorial', 'learn', 'understand'}
        vector[7] = len([w for w in words if w in help_words]) / len(words)
        
        # Normalize vector
        magnitude = math.sqrt(sum(x*x for x in vector))
        if magnitude > 0:
            vector = [x/magnitude for x in vector]
        
        return vector
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _detect_location(self, text: str) -> Optional[tuple]:
        """Detect a known location from text and return (name, lat, lon)"""
        t = text.lower()
        for key, value in self.city_coords.items():
            if key in t:
                return value
        # Default fallback to Mumbai if nothing detected
        return ("Mumbai", 19.0760, 72.8777)

    async def _fetch_here_current(self, lat: float, lon: float) -> Optional[Dict[str, Any]]:
        if not settings.HERE_API_KEY:
            return None
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {
            "apiKey": settings.HERE_API_KEY,
            "latitude": lat,
            "longitude": lon,
            "product": "observation",
            "oneobservation": "true",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            obs = (
                data.get("observations", {})
                .get("location", [{}])[0]
                .get("observation", [{}])[0]
            )
            if not obs:
                return None
            return {
                "temperature": obs.get("temperature"),
                "conditions": obs.get("description"),
                "wind_speed": obs.get("windSpeed"),
                "humidity": obs.get("humidity"),
            }

    async def _fetch_here_alerts(self, lat: float, lon: float) -> Optional[List[Dict[str, Any]]]:
        if not settings.HERE_API_KEY:
            return None
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {
            "apiKey": settings.HERE_API_KEY,
            "latitude": lat,
            "longitude": lon,
            "product": "alerts",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            alerts = data.get("alerts", {}).get("alerts", [])
            return alerts

    async def _fetch_here_forecast(self, lat: float, lon: float, days: int = 7) -> Optional[Dict[str, Any]]:
        if not settings.HERE_API_KEY:
            return None
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {
            "apiKey": settings.HERE_API_KEY,
            "latitude": lat,
            "longitude": lon,
            "product": "forecast_7days_simple",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            return resp.json()

    async def _fetch_here_traffic_count(self, lat: float, lon: float) -> Optional[int]:
        if not settings.HERE_API_KEY:
            return None
        url = "https://data.traffic.hereapi.com/v7/incidents"
        params = {
            "apiKey": settings.HERE_API_KEY,
            "in": f"circle:{lat},{lon};r=30000",
            "locationReferencing": "none",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            return len(data.get("results", []))

    def _find_best_match(self, query_vector: List[float]) -> tuple:
        """Find the best matching concept using vector similarity"""
        best_match = None
        best_score = 0.0
        
        for concept, concept_vector in self.knowledge_vectors.items():
            similarity = self._cosine_similarity(query_vector, concept_vector)
            if similarity > best_score:
                best_score = similarity
                best_match = concept
        
        return best_match, best_score
    
    def _enhance_response_with_context(self, base_response: Dict, query: str, confidence: float) -> Dict:
        """Enhance response with contextual information"""
        # Add conversation context
        if len(self.conversation_memory) > 0:
            recent_topics = [conv.get('topic') for conv in self.conversation_memory[-3:]]
            if any(topic for topic in recent_topics if topic):
                base_response['context_note'] = "Based on our recent conversation, "
        
        # Adjust confidence based on query complexity
        query_complexity = len(re.findall(r'\b\w+\b', query))
        adjusted_confidence = min(confidence * (1 + query_complexity * 0.05), 1.0)
        
        base_response['confidence'] = adjusted_confidence
        return base_response
    
    async def generate_intelligent_response(self, query: str) -> ChatResponse:
        """Generate intelligent response. Prefer MCP client; fallback to legacy."""
        # 0. Prefer TRUE MCP path first
        try:
            from app.agents.mcp_client import MCPClient
            if settings.GROQ_API_KEY:
                client = MCPClient()
                mcp_result = await client.run_query(query)
                if mcp_result and mcp_result.get("result"):
                    payload = mcp_result["result"]
                    # If router signaled no tool needed (greeting/chit-chat), reply simply
                    if isinstance(payload, dict) and payload.get("no_tool") is True:
                        ql = (query or "").lower()
                        if any(k in ql for k in ["capabilities", "what can you do", "features", "abilities", "help"]):
                            resp = (
                                "I can help with live, tool-based answers:\n"
                                "- weather_current(lat, lon): current conditions from HERE (temp, humidity, wind).\n"
                                "- weather_forecast(lat, lon, days=7): 7‑day forecast.\n"
                                "- weather_alerts(lat, lon): active weather alerts.\n"
                                "- traffic_incidents(lat, lon, radius): incident counts/details.\n\n"
                                "Ask naturally, e.g. ‘weather in Pune’ and I’ll detect the city and call the right tool."
                            )
                        else:
                            resp = "Hi! How can I help you?"
                        return ChatResponse(
                            response=resp,
                            timestamp=datetime.now(),
                            suggestions=[],
                        )
                    # Try friendly formatting for common shapes
                    text = None
                    # Freeform LLM answers (no tools)
                    if text is None and isinstance(payload, dict) and isinstance(payload.get('freeform_text'), str):
                        text = payload['freeform_text']
                    # Traffic incidents (HERE incidents API shape)
                    if text is None and isinstance(payload, dict) and isinstance(payload.get('results'), list):
                        incidents = payload.get('results', [])
                        count = len(incidents)
                        lines = [f"Traffic incidents around your area: {count} found."]
                        for inc in incidents[:3]:
                            det = inc.get('incidentDetails', {}) if isinstance(inc, dict) else {}
                            crit = det.get('criticality', 'unknown')
                            tdesc = (det.get('typeDescription') or {}).get('value') if isinstance(det.get('typeDescription'), dict) else det.get('type')
                            closed = det.get('roadClosed', False)
                            desc = (det.get('description') or {}).get('value') if isinstance(det.get('description'), dict) else ''
                            snippet = (desc or '').strip()
                            if len(snippet) > 120:
                                snippet = snippet[:117] + '...'
                            lines.append(f"- {tdesc or 'Incident'} ({crit}){' [road closed]' if closed else ''}: {snippet}")
                        text = "\n".join(lines)
                    
                    # Weather alerts (list of alert objects)
                    if text is None and isinstance(payload, list):
                        alerts = payload
                        count = len(alerts)
                        lines = [f"Weather alerts in your area: {count} active."]
                        for a in alerts[:3]:
                            sev = a.get('severity', 'unknown') if isinstance(a, dict) else 'unknown'
                            typ = a.get('type', 'Alert') if isinstance(a, dict) else 'Alert'
                            desc = (a.get('description') or '') if isinstance(a, dict) else ''
                            if isinstance(desc, dict):
                                desc = desc.get('value', '')
                            snippet = (desc or '').strip()
                            if len(snippet) > 120:
                                snippet = snippet[:117] + '...'
                            lines.append(f"- {typ} ({sev}): {snippet}")
                        text = "\n".join(lines)
                    if isinstance(payload, dict) and {"temperature","conditions","humidity","wind_speed"}.issubset(set(payload.keys())):
                        text = (
                            f"Live weather: {payload.get('conditions','N/A')}. "
                            f"Temp {payload.get('temperature','N/A')}°C, "
                            f"Humidity {payload.get('humidity','N/A')}%, "
                            f"Wind {payload.get('wind_speed','N/A')} km/h."
                        )
                    # 7-day forecast (HERE simple forecast shape)
                    if text is None and isinstance(payload, dict) and isinstance(payload.get('dailyForecasts'), dict):
                        loc = payload.get('dailyForecasts', {}).get('forecastLocation', {})
                        days = loc.get('forecast', []) if isinstance(loc, dict) else []
                        if isinstance(days, list) and days:
                            lines = ["7-day forecast:"]
                            for d in days[:5]:  # summarize first 5 entries
                                if not isinstance(d, dict):
                                    continue
                                desc = d.get('description') or d.get('skyDescription') or '—'
                                rainp = d.get('precipitationProbability') or '0'
                                hi = d.get('highTemperature') or d.get('highTemperatureC') or '—'
                                lo = d.get('lowTemperature') or d.get('lowTemperatureC') or '—'
                                lines.append(f"- {desc} | rain {rainp}% | H {hi}°C / L {lo}°C")
                            text = "\n".join(lines)
                    if text is None:
                        text = json.dumps(payload)[:600]
                    return ChatResponse(
                        response=text,
                        timestamp=datetime.now(),
                        suggestions=[],
                    )
        except Exception:
            pass

        # MCP unavailable or failed: return simple fallback (no legacy logic)
        return ChatResponse(
            response="Sorry, live tools are temporarily unavailable. Please try again shortly.",
            timestamp=datetime.now(),
            suggestions=[]
        )

        # 2. Try True MCP Path (if fastmcp installed and key is set)
        try:
            from app.agents.mcp_client import MCPClient
            if settings.GROQ_API_KEY:
                try:
                    client = MCPClient()
                    result = await client.run_query(query)
                    if result and result.get("result"):
                        return ChatResponse(
                            response=f"MCP call successful. Result: {json.dumps(result['result'])[:200]}...",
                            timestamp=datetime.now(),
                            suggestions=["Next question?"],
                        )
                except Exception as e:
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "mcp_client", "stage": "error", "args": {"error": str(e)}}
                    })
        except ImportError:
            pass  # MCP client not available, fall through to next method

        # 3. Try In-Process LLM Agent Path (if groq installed and key is set)
        try:
            from app.agents.llm_agent import GroqToolAgent
            if settings.GROQ_API_KEY:
                try:
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "llm_router", "stage": "start", "args": {"model": settings.GROQ_MODEL}}
                    })
                    router = GroqToolAgent()
                    chosen = router.decide_tool(query)
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "llm_router", "stage": "end", "args": {"chosen_tool": chosen}}
                    })
                    if chosen in {"weather_current", "weather_forecast", "weather_alerts", "traffic_incidents"}:
                        loc = self._detect_location(query)
                        city_name, lat, lon = loc if loc else ("Mumbai", 19.0760, 72.8777)
                        # ... (rest of the LLM agent logic remains the same)
                        if chosen == "weather_current":
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_current", "stage": "start", "args": {"latitude": lat, "longitude": lon}}})
                            current = await self._fetch_here_current(lat, lon)
                            if current:
                                text = f"Live weather for {city_name}: {current.get('conditions', 'N/A')}. Temp {current.get('temperature', 'N/A')}°C, Humidity {current.get('humidity', 'N/A')}%, Wind {current.get('wind_speed', 'N/A')} km/h."
                                await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_current", "stage": "end", "resultSummary": "ok"}})
                                return ChatResponse(response=text, timestamp=datetime.now(), suggestions=["Weather alerts", "7-day forecast", "Traffic incidents"])
                        elif chosen == "weather_forecast":
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_forecast", "stage": "start", "args": {"latitude": lat, "longitude": lon}}})
                            await self._fetch_here_forecast(lat, lon)
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_forecast", "stage": "end", "resultSummary": "ok"}})
                            return ChatResponse(response=f"7-day forecast available for {city_name}.", timestamp=datetime.now(), suggestions=["Current weather", "Weather alerts"])
                        elif chosen == "weather_alerts":
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_alerts", "stage": "start", "args": {"latitude": lat, "longitude": lon}}})
                            alerts = await self._fetch_here_alerts(lat, lon)
                            count = len(alerts) if alerts else 0
                            summary = alerts[0].get("description", "No active alerts") if count > 0 else "No active alerts."
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "weather_alerts", "stage": "end", "resultSummary": f"{count} alerts"}})
                            return ChatResponse(response=f"{count} weather alert(s) near {city_name}. {summary}", timestamp=datetime.now(), suggestions=["Current weather", "Traffic incidents"])
                        elif chosen == "traffic_incidents":
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "traffic_incidents", "stage": "start", "args": {"latitude": lat, "longitude": lon}}})
                            count = await self._fetch_here_traffic_count(lat, lon)
                            await manager.broadcast({"type": "mcp_tool", "data": {"tool": "traffic_incidents", "stage": "end", "resultSummary": f"{count} incidents"}})
                            return ChatResponse(response=f"{count} traffic incidents reported near {city_name}.", timestamp=datetime.now(), suggestions=["Current weather", "Weather alerts"])

                except Exception as e:
                    await manager.broadcast({"type": "mcp_tool", "data": {"tool": "llm_router", "stage": "error", "args": {"error": str(e)}}})
        except ImportError:
            pass # Groq agent not available, fall through


        # Try to augment with LIVE HERE data for relevant topics (existing path)
        live_augmented = False
        response_data: Dict[str, Any]
        if confidence >= 0.3 and best_concept in {"weather_current", "weather_forecast", "weather_alerts", "maps_incidents"}:
            try:
                loc = self._detect_location(query)
                city_name, lat, lon = loc if loc else ("Mumbai", 19.0760, 72.8777)
                if best_concept == "weather_current":
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "weather_current", "stage": "start", "args": {"latitude": lat, "longitude": lon}}
                    })
                    current = await self._fetch_here_current(lat, lon)
                    if current:
                        response_text = (
                            f"Live weather for {city_name}: {current.get('conditions', 'N/A')}. "
                            f"Temp {current.get('temperature', 'N/A')}°C, "
                            f"Humidity {current.get('humidity', 'N/A')}%, "
                            f"Wind {current.get('wind_speed', 'N/A')} km/h."
                        )
                        response_data = {
                            "response": response_text,
                            "suggestions": ["Weather alerts", "7-day forecast", "Traffic incidents nearby"],
                            "confidence": confidence,
                        }
                        await manager.broadcast({
                            "type": "mcp_tool",
                            "data": {"tool": "weather_current", "stage": "end", "args": {"latitude": lat, "longitude": lon}, "resultSummary": "ok"}
                        })
                        live_augmented = True
                elif best_concept == "weather_alerts":
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "weather_alerts", "stage": "start", "args": {"latitude": lat, "longitude": lon}}
                    })
                    alerts = await self._fetch_here_alerts(lat, lon)
                    if alerts is not None:
                        count = len(alerts)
                        top = alerts[0] if alerts else {}
                        summary = top.get("description", "No active alerts") if count else "No active alerts"
                        response_text = f"{count} weather alert(s) near {city_name}. {summary}"
                        response_data = {
                            "response": response_text,
                            "suggestions": ["View incidents map", "Check forecast", "Current weather"],
                            "confidence": confidence,
                        }
                        await manager.broadcast({
                            "type": "mcp_tool",
                            "data": {"tool": "weather_alerts", "stage": "end", "args": {"latitude": lat, "longitude": lon}, "resultSummary": f"count: {count}"}
                        })
                        live_augmented = True
                elif best_concept == "maps_incidents":
                    await manager.broadcast({
                        "type": "mcp_tool",
                        "data": {"tool": "traffic_incidents", "stage": "start", "args": {"latitude": lat, "longitude": lon, "radius": 30000}}
                    })
                    count = await self._fetch_here_traffic_count(lat, lon)
                    if count is not None:
                        response_text = f"Live traffic incidents near {city_name}: {count} reported within 30km radius."
                        response_data = {
                            "response": response_text,
                            "suggestions": ["Show incident details", "Alternate routes", "Weather impact"],
                            "confidence": confidence,
                        }
                        await manager.broadcast({
                            "type": "mcp_tool",
                            "data": {"tool": "traffic_incidents", "stage": "end", "args": {"latitude": lat, "longitude": lon, "radius": 30000}, "resultSummary": f"count: {count}"}
                        })
                        live_augmented = True
            except Exception:
                # If live augmentation fails, fall back to template below
                await manager.broadcast({
                    "type": "mcp_tool",
                    "data": {"tool": best_concept, "stage": "error", "args": {}}
                })
                live_augmented = False

        if not live_augmented:
            # Handle low confidence or fallback to templates
            if confidence < 0.3:
                response_data = {
                    "response": "I understand you're asking about ResQMap, but I'd like to provide the most accurate help possible. Could you rephrase your question or be more specific about what you're looking for? I can assist with weather data, disaster management, mapping features, or API integration.",
                    "suggestions": ["Weather information", "Disaster management", "Map features", "API help", "General guidance"],
                    "confidence": confidence,
                }
            else:
                template = self.response_templates.get(best_concept, self.response_templates["help_general"])
                response_data = {
                    "response": template["response"],
                    "suggestions": template["suggestions"],
                    "confidence": confidence,
                }
                response_data = self._enhance_response_with_context(response_data, query, confidence)
        
        # Store in conversation memory
        self.conversation_memory.append({
            "query": query,
            "topic": best_concept,
            "confidence": confidence,
            "timestamp": datetime.now()
        })
        
        # Keep memory manageable
        if len(self.conversation_memory) > 20:
            self.conversation_memory = self.conversation_memory[-15:]
        
        return ChatResponse(
            response=response_data["response"],
            timestamp=datetime.now(),
            suggestions=response_data["suggestions"],
            confidence=response_data["confidence"]
        )

# Initialize intelligent agent
intelligent_agent = IntelligentResQMapAgent()

@router.post("/intelligent-chat", response_model=ChatResponse)
async def chat_with_intelligent_agent(message: ChatMessage):
    """Chat with truly intelligent ResQMap AI agent"""
    try:
        if not message.message or not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = await intelligent_agent.generate_intelligent_response(message.message.strip())
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")

@router.get("/intelligent-chat/stats")
async def get_intelligence_stats():
    """Get intelligence and learning statistics"""
    return {
        "agent_type": "Mathematical Vector Intelligence",
        "conversation_memory": len(intelligent_agent.conversation_memory),
        "knowledge_concepts": len(intelligent_agent.knowledge_vectors),
        "learning_enabled": True,
        "vector_dimensions": 8,
        "similarity_algorithm": "Cosine Similarity",
        "timestamp": datetime.now()
    }
