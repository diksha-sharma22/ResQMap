from fastapi import WebSocket
from typing import Dict, List
import json


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
    
    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)
    
    async def broadcast_alert(self, alert: dict):
        """Broadcast disaster alerts to all connected clients"""
        message = {
            "type": "alert",
            "data": alert
        }
        await self.broadcast(message)
    
    async def broadcast_map_update(self, update: dict):
        """Broadcast map updates"""
        message = {
            "type": "map_update",
            "data": update
        }
        await self.broadcast(message)


manager = ConnectionManager()
