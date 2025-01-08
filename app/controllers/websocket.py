from fastapi import WebSocket, WebSocketDisconnect
from ..services.number_generator import NumberGenerator
from ..database import SessionLocal
import asyncio

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            db = SessionLocal()
            try:
                number_gen = NumberGenerator()
                value = number_gen.generate()
                number = number_gen.save_number(db, value)
                
                await manager.broadcast({
                    "timestamp": number.timestamp.isoformat(),
                    "value": number.value
                })
            finally:
                db.close()
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)