import asyncio
from typing import Any, Dict

import httpx

# Guarded import for resilience
try:
    from fastmcp import FastMCP, tool
    from fastmcp.server import run_stdio_server
except ImportError:
    print("FastMCP not installed. Run 'pip install fastmcp' to enable MCP server.")
    FastMCP = None
    tool = None
    run_stdio_server = None

# Use a separate settings instance to avoid circular imports if needed
# For simplicity, we assume direct import is fine for now.
try:
    from app.core.config import settings
except ImportError:
    # Fallback for running standalone without the full app structure in PYTHONPATH
    print("Could not import FastAPI settings. Standalone mode.")
    from pydantic_settings import BaseSettings

    class StandaloneSettings(BaseSettings):
        HERE_API_KEY: str = "e8lygiADBgeCaJQXzBQfye6L1lFSrXp5km7f205iJaA"
        HERE_BASE_URL: str = "https://weather.cc.api.here.com/weather/1.0"

        class Config:
            env_file = ".env"

    settings = StandaloneSettings()


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


if FastMCP:
    server = FastMCP(
        name="resqmap.tools",
        title="ResQMap Disaster Intelligence Tools",
        description="Live data tools for weather, alerts, and traffic.",
    )

    @tool(server)
    async def weather_current(latitude: float, longitude: float) -> Dict[str, Any]:
        """Get current weather observation from HERE Weather API."""
        await _emit_telemetry("weather_current", "start", {"latitude": latitude, "longitude": longitude})
        # This logic should be identical to the one in intelligent_agent.py
        # For brevity, we are calling a simplified version here.
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {"apiKey": settings.HERE_API_KEY, "latitude": latitude, "longitude": longitude, "product": "observation"}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            await _emit_telemetry("weather_current", "end", summary="Success")
            return r.json()

    @tool(server)
    async def weather_forecast(latitude: float, longitude: float, days: int = 7) -> Dict[str, Any]:
        """Get 7-day weather forecast from HERE Weather API."""
        await _emit_telemetry("weather_forecast", "start", {"latitude": latitude, "longitude": longitude, "days": days})
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {"apiKey": settings.HERE_API_KEY, "latitude": latitude, "longitude": longitude, "product": "forecast_7days_simple"}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            await _emit_telemetry("weather_forecast", "end", summary="Success")
            return r.json()

    @tool(server)
    async def weather_alerts(latitude: float, longitude: float) -> Dict[str, Any]:
        """Get severe weather alerts from HERE Weather API."""
        await _emit_telemetry("weather_alerts", "start", {"latitude": latitude, "longitude": longitude})
        url = f"{settings.HERE_BASE_URL}/report.json"
        params = {"apiKey": settings.HERE_API_KEY, "latitude": latitude, "longitude": longitude, "product": "alerts"}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            await _emit_telemetry("weather_alerts", "end", summary="Success")
            return r.json()

    @tool(server)
    async def traffic_incidents(latitude: float, longitude: float, radius: int = 50000) -> Dict[str, Any]:
        """Get live traffic incidents from HERE Traffic API."""
        await _emit_telemetry("traffic_incidents", "start", {"latitude": latitude, "longitude": longitude, "radius": radius})
        url = "https://data.traffic.hereapi.com/v7/incidents"
        params = {"apiKey": settings.HERE_API_KEY, "in": f"circle:{latitude},{longitude};r={radius}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            await _emit_telemetry("traffic_incidents", "end", summary="Success")
            return r.json()

async def main():
    if run_stdio_server and server:
        await run_stdio_server(server)

if __name__ == "__main__":
    asyncio.run(main())
