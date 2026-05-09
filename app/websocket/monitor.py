from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/live-monitoring")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # In a real app, this might trigger a background task to process the data
            # Here we just echo back a simulated analysis
            try:
                sensor_payload = json.loads(data)
                alert = None
                if sensor_payload.get("crack_sensor", 0) > 2.0:
                    alert = {"type": "Crack Expansion", "severity": "Critical"}
                
                response = {
                    "status": "received",
                    "echo": sensor_payload,
                    "alert": alert
                }
                await manager.send_personal_message(json.dumps(response), websocket)
            except json.JSONDecodeError:
                await manager.send_personal_message("Invalid JSON format", websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
