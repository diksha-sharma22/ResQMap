import asyncio
from typing import Any, Dict, List, Optional

import httpx
from app.core.config import settings

# MCP server primitives
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
except Exception as e:
    raise RuntimeError(
        "The 'mcp' package is required. Please add it to your environment: pip install mcp"
    ) from e

server = Server("resqmap")

HERE_WEATHER_BASE = settings.HERE_BASE_URL.rstrip("/")
HERE_TRAFFIC_URL = "https://data.traffic.hereapi.com/v7/incidents"

# Telemetry endpoint (FastAPI backend should be running here)
TELEMETRY_URL = "http://127.0.0.1:8000/api/telemetry/mcp-tool-log"


async def _emit_tool_log(
    tool: str,
    stage: str,
    args: Optional[Dict[str, Any]] = None,
    result_summary: Optional[str] = None,
) -> None:
    """Best-effort telemetry POST to backend to visualize tool activity."""
    payload = {
        "tool": tool,
        "stage": stage,
        "args": args or {},
        "resultSummary": (result_summary or "")[:500],
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(TELEMETRY_URL, json=payload, timeout=3.0)
    except Exception:
        # Never fail the tool because of telemetry issues
        pass


async def _fetch_here_current(lat: float, lon: float) -> Dict[str, Any]:
    if not settings.HERE_API_KEY:
        return {
            "mock_data": True,
            "message": "HERE API Key not configured",
            "temperature": 28,
            "conditions": "Partly Cloudy",
            "wind_speed": 15,
            "humidity": 72,
            "pressure": 1012,
        }
    url = f"{HERE_WEATHER_BASE}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": lat,
        "longitude": lon,
        "product": "observation",
        "oneobservation": "true",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        obs = (
            data.get("observations", {})
            .get("location", [{}])[0]
            .get("observation", [{}])[0]
        )
        return {
            "temperature": obs.get("temperature"),
            "conditions": obs.get("description"),
            "wind_speed": obs.get("windSpeed"),
            "humidity": obs.get("humidity"),
            "pressure": obs.get("barometerPressure"),
            "visibility": obs.get("visibility"),
            "comfort": obs.get("comfort"),
        }


async def _fetch_here_forecast(lat: float, lon: float, days: int = 7) -> Dict[str, Any]:
    if not settings.HERE_API_KEY:
        return {
            "mock_data": True,
            "message": "HERE API Key not configured",
            "forecast": [],
        }
    url = f"{HERE_WEATHER_BASE}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": lat,
        "longitude": lon,
        "product": "forecast_7days_simple",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=10.0)
        r.raise_for_status()
        return r.json()


async def _fetch_here_alerts(lat: float, lon: float) -> Dict[str, Any]:
    if not settings.HERE_API_KEY:
        return {
            "mock_data": True,
            "message": "HERE API Key not configured",
            "alerts": [],
        }
    url = f"{HERE_WEATHER_BASE}/report.json"
    params = {
        "apiKey": settings.HERE_API_KEY,
        "latitude": lat,
        "longitude": lon,
        "product": "alerts",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        alerts = data.get("alerts", {}).get("alerts", [])
        formatted = []
        for alert in alerts:
            formatted.append({
                "type": alert.get("type", "Weather Alert"),
                "severity": alert.get("severity", "Unknown"),
                "description": alert.get("description", ""),
                "valid_from": alert.get("validTimeLocal", ""),
                "valid_until": alert.get("expireTimeLocal", ""),
            })
        return {"alerts": formatted, "count": len(formatted)}


async def _fetch_here_traffic(lat: float, lon: float, radius: int = 50000) -> Dict[str, Any]:
    if not settings.HERE_API_KEY:
        return {
            "mock_data": True,
            "message": "HERE API Key not configured",
            "incidents": [],
        }
    params = {
        "apiKey": settings.HERE_API_KEY,
        "in": f"circle:{lat},{lon};r={radius}",
        "locationReferencing": "none",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(HERE_TRAFFIC_URL, params=params, timeout=10.0)
        r.raise_for_status()
        data = r.json()
        incidents = []
        for item in data.get("results", []):
            incident = item.get("incident", {})
            location = item.get("location", {})
            geo = (
                location.get("shape", {}).get("links", [{}])[0].get("points", [{}])[0]
                if location.get("shape", {}).get("links")
                else {}
            )
            incident_type = incident.get("type", {}).get("description", "Traffic Incident")
            description = incident.get("description", {}).get("value", "Traffic disruption")
            incidents.append({
                "id": item.get("incidentId", "unknown"),
                "type": incident_type,
                "description": description,
                "severity": incident.get("criticality", {}).get("description", "minor"),
                "start_time": incident.get("startTime", ""),
                "end_time": incident.get("endTime", ""),
                "latitude": geo.get("lat", lat),
                "longitude": geo.get("lng", lon),
            })
        return {"incidents": incidents, "count": len(incidents)}


@server.tool()
async def weather_current(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get current weather observation from HERE Weather API"""
    await _emit_tool_log("weather_current", "start", {"latitude": latitude, "longitude": longitude})
    try:
        result = await _fetch_here_current(latitude, longitude)
        await _emit_tool_log("weather_current", "end", result_summary=f"keys: {list(result.keys())}")
        return result
    except Exception as e:
        await _emit_tool_log("weather_current", "error", result_summary=str(e))
        raise


@server.tool()
async def weather_forecast(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
    """Get 7-day weather forecast from HERE Weather API"""
    await _emit_tool_log("weather_forecast", "start", {"latitude": latitude, "longitude": longitude, "days": days})
    try:
        result = await _fetch_here_forecast(latitude, longitude, days)
        await _emit_tool_log("weather_forecast", "end", result_summary=f"ok")
        return result
    except Exception as e:
        await _emit_tool_log("weather_forecast", "error", result_summary=str(e))
        raise


@server.tool()
async def weather_alerts(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get severe weather alerts from HERE Weather API"""
    await _emit_tool_log("weather_alerts", "start", {"latitude": latitude, "longitude": longitude})
    try:
        result = await _fetch_here_alerts(latitude, longitude)
        await _emit_tool_log("weather_alerts", "end", result_summary=f"count: {result.get('count', 'n/a')}")
        return result
    except Exception as e:
        await _emit_tool_log("weather_alerts", "error", result_summary=str(e))
        raise


@server.tool()
async def traffic_incidents(latitude: float, longitude: float, radius: int = 50000) -> Dict[str, Any]:
    """Get live traffic incidents from HERE Traffic API"""
    await _emit_tool_log("traffic_incidents", "start", {"latitude": latitude, "longitude": longitude, "radius": radius})
    try:
        result = await _fetch_here_traffic(latitude, longitude, radius)
        await _emit_tool_log("traffic_incidents", "end", result_summary=f"count: {result.get('count', 'n/a')}")
        return result
    except Exception as e:
        await _emit_tool_log("traffic_incidents", "error", result_summary=str(e))
        raise


async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)


if __name__ == "__main__":
    import anyio

    anyio.run(_main)
