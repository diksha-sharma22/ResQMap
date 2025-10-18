from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

from app.core.websocket_manager import manager

router = APIRouter()


class McpToolLog(BaseModel):
    tool: str
    stage: str  # "start" | "end" | "error"
    args: Optional[Dict[str, Any]] = None
    resultSummary: Optional[str] = None
    timestamp: Optional[str] = None
    client_id: Optional[str] = None


@router.post("/mcp-tool-log")
async def mcp_tool_log(event: McpToolLog):
    """Receive MCP tool invocation logs and broadcast to connected clients."""
    message = {
        "type": "mcp_tool",
        "data": {
            "tool": event.tool,
            "stage": event.stage,
            "args": event.args or {},
            "resultSummary": event.resultSummary or "",
            "timestamp": event.timestamp or datetime.utcnow().isoformat(),
            "client_id": event.client_id,
        },
    }
    await manager.broadcast(message)
    return {"status": "ok"}
