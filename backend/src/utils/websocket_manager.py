from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_to_user(self, message: Dict[str, Any], user_id: str):
        if user_id in self.user_connections:
            await self.send_personal_message(message, self.user_connections[user_id])
    
    async def broadcast(self, message: Dict[str, Any]):
        if self.active_connections:
            tasks = []
            for connection in self.active_connections.copy():
                try:
                    tasks.append(self.send_personal_message(message, connection))
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    self.active_connections.remove(connection)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def stream_agent_response(self, websocket: WebSocket, agent_response: str, agent_name: str):
        words = agent_response.split()
        
        for i, word in enumerate(words):
            message = {
                "type": "agent_stream",
                "agent": agent_name,
                "content": word + " ",
                "is_complete": i == len(words) - 1,
                "progress": (i + 1) / len(words)
            }
            
            await self.send_personal_message(message, websocket)
            await asyncio.sleep(0.05)

# Global manager instance
manager = ConnectionManager()