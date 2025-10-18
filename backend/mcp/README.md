# ResQMap MCP Server

This MCP server exposes ResQMap's live HERE-backed tools to any MCP-compatible client (stdio transport).

## Tools
- weather_current(latitude: float, longitude: float)
- weather_forecast(latitude: float, longitude: float, days: int = 7)
- weather_alerts(latitude: float, longitude: float)
- traffic_incidents(latitude: float, longitude: float, radius: int = 50000)

All tools read HERE_API_KEY from your existing FastAPI settings via `app.core.config.settings`.

## Prerequisites
- Set `HERE_API_KEY` in `backend/.env`
- Install backend deps:

```powershell
# From project root or backend directory
pip install -r backend/requirements-minimal.txt
```

## Run
Run from the `backend` directory so Python can import `app.*` modules:

```powershell
# Option A: module
python -m mcp.server

# Option B: script
python mcp/server.py
```

This starts an MCP stdio server named `resqmap`. Point your MCP client to the launched process using stdio transport.

## Notes
- If `HERE_API_KEY` is missing, the server returns lightweight mock responses for weather/alerts/traffic tools instead of failing hard.
- The implementation mirrors logic in `app/api/weather.py` to ensure consistent outputs.
