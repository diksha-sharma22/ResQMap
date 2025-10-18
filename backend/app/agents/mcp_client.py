import asyncio
import json
import subprocess
from typing import Any, Dict, Optional

import httpx
from groq import Groq

from app.core.config import settings

TELEMETRY_URL = "http://127.0.0.1:8000/api/telemetry/mcp-tool-log"


async def _emit_telemetry(tool_name: str, stage: str, args: Dict = None, summary: str = ""):
    payload = {
        "tool": tool_name,
        "stage": stage,
        "args": args or {},
        "resultSummary": summary,
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(TELEMETRY_URL, json=payload, timeout=3.0)
    except Exception:
        pass  # Best-effort


class MCPClient:
    """LLM-driven MCP client that picks a valid MCP tool and executes it.
    - Only allowed tools: weather_current, weather_forecast, weather_alerts, traffic_incidents
    - Auto-derives lat/lon from a built-in city list when user provides a location name.
    """

    CITY_COORDS: Dict[str, tuple] = {
        "mumbai": (19.0760, 72.8777),
        "pune": (18.5204, 73.8567),
        "delhi": (28.6139, 77.2090),
        "chennai": (13.0827, 80.2707),
        "bangalore": (12.9716, 77.5946),
        "bengaluru": (12.9716, 77.5946),
        "ahmedabad": (23.0225, 72.5714),
        "kolkata": (22.5726, 88.3639),
        "hyderabad": (17.3850, 78.4867),
        "jaipur": (26.9124, 75.7873),
    }

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY must be set")
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    async def _freeform_answer(self, query: str) -> str:
        """Use the LLM to answer general questions when no tool is needed."""
        await _emit_telemetry("llm_freeform", "start", {"model": self.model})
        system = (
            "You are ResQMap's assistant. Answer clearly and concisely.\n"
            "If the user asks for live weather/traffic, do NOT fabricate data—say you can fetch it if they specify a city."
        )
        completion = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": query},
            ],
            temperature=0.3,
            max_tokens=256,
        )
        text = completion.choices[0].message.content.strip()
        await _emit_telemetry("llm_freeform", "end", summary=(text[:80] + ("…" if len(text) > 80 else "")))
        return text

    async def _decide_tool(self, query: str) -> Optional[Dict[str, Any]]:
        await _emit_telemetry("llm_router(mcp)", "start", {"model": self.model})
        system = (
            "You are a strict tool router for a disaster intelligence MCP server.\n"
            "Allowed tools (choose at most one): \n"
            "- weather_current(latitude: number, longitude: number)\n"
            "- weather_forecast(latitude: number, longitude: number, days: number=7)\n"
            "- weather_alerts(latitude: number, longitude: number)\n"
            "- traffic_incidents(latitude: number, longitude: number, radius: number=50000)\n\n"
            "If the user intent is greeting/chit-chat with no weather/traffic need, return {\"tool_name\": \"no_tool\"}.\n"
            "If the user gives a city name (e.g., Pune), include it in 'parameters.location'.\n"
            "Output ONLY valid JSON: {\"tool_name\": <string>, \"parameters\": <object>} (parameters may be empty).\n"
            "Never invent tools. Never include commentary."
        )
        completion = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": query}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        await _emit_telemetry("llm_router(mcp)", "end", summary=content)
        return json.loads(content)

    def _normalize_params(self, decided: Dict[str, Any]) -> Dict[str, Any]:
        params = decided.get("parameters", {}) or {}
        # Treat missing or zero coordinates as missing
        if ("latitude" not in params or "longitude" not in params or not params.get("latitude") or not params.get("longitude")):
            loc = (params.get("location") or params.get("city") or params.get("place") or "").strip().lower()
            if loc in self.CITY_COORDS:
                lat, lon = self.CITY_COORDS[loc]
                params["latitude"] = lat
                params["longitude"] = lon
            else:
                params.setdefault("latitude", 19.0760)
                params.setdefault("longitude", 72.8777)
        return params

    async def run_query(self, query: str) -> Optional[Dict[str, Any]]:
        decided = await self._decide_tool(query)
        if not decided or "tool_name" not in decided:
            return None
        tool_name = decided["tool_name"]
        if tool_name in {"no_tool", "none"}:
            # No tool needed: answer naturally using the LLM
            text = await self._freeform_answer(query)
            return {"result": {"freeform_text": text}}
        if tool_name not in {"weather_current", "weather_forecast", "weather_alerts", "traffic_incidents"}:
            await _emit_telemetry("mcp_client", "error", {"error": "invalid_tool", "tool": tool_name})
            return None
        params = self._normalize_params(decided)

        await _emit_telemetry("mcp_trace", "start", {"tool": tool_name, "params": params})
        # Execute directly (until MCP stdio is fully wired). Uses HERE-backed executors.
        direct = await self._fallback_execute(tool_name, params)
        await _emit_telemetry("mcp_trace", "end", {"tool": tool_name}, summary=("ok" if direct else "error"))
        return direct

    async def _fallback_execute(self, tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute tool directly against HERE APIs if MCP stdio path is unavailable."""
        if not settings.HERE_API_KEY:
            return None
        lat = params.get("latitude", 19.0760)
        lon = params.get("longitude", 72.8777)
        try:
            if tool_name == "weather_current":
                url = f"{settings.HERE_BASE_URL}/report.json"
                q = {"apiKey": settings.HERE_API_KEY, "latitude": lat, "longitude": lon, "product": "observation", "oneobservation": "true"}
                async with httpx.AsyncClient() as client:
                    r = await client.get(url, params=q, timeout=10.0)
                    r.raise_for_status()
                    data = r.json()
                    obs = (data.get("observations", {}).get("location", [{}])[0].get("observation", [{}])[0])
                    return {"result": {"temperature": obs.get("temperature"), "conditions": obs.get("description"), "humidity": obs.get("humidity"), "wind_speed": obs.get("windSpeed")}}
            if tool_name == "weather_forecast":
                url = f"{settings.HERE_BASE_URL}/report.json"
                q = {"apiKey": settings.HERE_API_KEY, "latitude": lat, "longitude": lon, "product": "forecast_7days_simple"}
                async with httpx.AsyncClient() as client:
                    r = await client.get(url, params=q, timeout=10.0)
                    r.raise_for_status()
                    return {"result": r.json()}
            if tool_name == "weather_alerts":
                url = f"{settings.HERE_BASE_URL}/report.json"
                q = {"apiKey": settings.HERE_API_KEY, "latitude": lat, "longitude": lon, "product": "alerts"}
                async with httpx.AsyncClient() as client:
                    r = await client.get(url, params=q, timeout=10.0)
                    r.raise_for_status()
                    data = r.json()
                    alerts = data.get("alerts", {}).get("alerts", [])
                    return {"result": alerts}
            if tool_name == "traffic_incidents":
                url = "https://data.traffic.hereapi.com/v7/incidents"
                q = {"apiKey": settings.HERE_API_KEY, "in": f"circle:{lat},{lon};r={params.get('radius',50000)}", "locationReferencing": "none"}
                async with httpx.AsyncClient() as client:
                    r = await client.get(url, params=q, timeout=10.0)
                    r.raise_for_status()
                    return {"result": r.json()}
        except Exception:
            return None
        return None
