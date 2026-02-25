from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Almacenar conexiones activas por conversación
active_connections: dict[int, List[WebSocket]] = {}

@router.websocket("/ws/conversation/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int):
    await websocket.accept()
    if conversation_id not in active_connections:
        active_connections[conversation_id] = []
    active_connections[conversation_id].append(websocket)
    logger.info(f"Cliente conectado a conversación {conversation_id}")
    
    try:
        while True:
            # Mantener la conexión viva (podríamos recibir mensajes del cliente si es necesario)
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections[conversation_id].remove(websocket)
        logger.info(f"Cliente desconectado de conversación {conversation_id}")

# Endpoints internos para que el worker notifique
@router.post("/internal/conversations/{conversation_id}/messages/notify")
async def notify_new_message(conversation_id: int, message_data: dict):
    """Recibe notificación del worker y la envía por WebSocket a los clientes."""
    if conversation_id in active_connections:
        for connection in active_connections[conversation_id]:
            try:
                await connection.send_json(message_data)
            except:
                # Si falla, probablemente la conexión está rota, la limpiamos después
                pass
    return {"ok": True}

@router.post("/internal/conversations/{conversation_id}/status/notify")
async def notify_status_change(conversation_id: int, data: dict):
    """Notifica cambio de estado de conversación."""
    if conversation_id in active_connections:
        message = {
            "type": "status_change",
            "status": data.get("status"),
            "conversation_id": conversation_id
        }
        for connection in active_connections[conversation_id]:
            try:
                await connection.send_json(message)
            except:
                pass
    return {"ok": True}