from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.socket_manager import emit_new_message, emit_conversation_updated

router = APIRouter(prefix="/internal", tags=["internal"])

class MessageNotification(BaseModel):
    conversation_id: int
    message_data: dict

class StatusNotification(BaseModel):
    conversation_id: int
    status: str

@router.post("/notify-message")
async def notify_message(notification: MessageNotification):
    """Endpoint para que el worker notifique nuevos mensajes vía WebSocket"""
    await emit_new_message(notification.conversation_id, notification.message_data)
    return {"status": "ok"}

@router.post("/notify-status")
async def notify_status(notification: StatusNotification):
    """Endpoint para que el worker notifique cambio de estado"""
    await emit_conversation_updated(notification.conversation_id, notification.status)
    return {"status": "ok"}