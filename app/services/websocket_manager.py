from fastapi import WebSocket
from typing import Dict
import asyncio
from ..models.number import RandomNumber
from ..services.number_generator import number_generator

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, number: RandomNumber, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(number.to_dict())

    async def stream_numbers(self, websocket: WebSocket, user_id: str, db):
        try:
            while True:
                latest = number_generator.get_latest(db)
                if latest:
                    await self.send_personal_message(latest, user_id)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error streaming numbers: {str(e)}")
            self.disconnect(user_id)

websocket_manager = WebSocketManager()