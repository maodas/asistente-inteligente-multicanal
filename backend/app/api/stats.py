from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/")
def get_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Devuelve estadísticas básicas del sistema.
    """
    # Total de conversaciones
    total_conversations = db.query(Conversation).count()
    
    # Conversaciones por estado
    conversations_by_status = {
        "bot": db.query(Conversation).filter(Conversation.status == ConversationStatus.BOT).count(),
        "human": db.query(Conversation).filter(Conversation.status == ConversationStatus.HUMAN).count(),
        "ended": db.query(Conversation).filter(Conversation.status == ConversationStatus.ENDED).count(),
    }
    
    # Total de mensajes
    total_messages = db.query(Message).count()
    
    # Mensajes por tipo de emisor
    messages_by_sender = {
        "customer": db.query(Message).filter(Message.sender == "customer").count(),
        "bot": db.query(Message).filter(Message.sender == "bot").count(),
        "human": db.query(Message).filter(Message.sender == "human").count(),
    }
    
    # Conversaciones en las últimas 24 horas
    last_24h = datetime.utcnow() - timedelta(hours=24)
    conversations_last_24h = db.query(Conversation).filter(Conversation.created_at >= last_24h).count()
    
    # Promedio de mensajes por conversación
    avg_messages_per_conversation = 0
    if total_conversations > 0:
        avg_messages_per_conversation = total_messages / total_conversations
    
    return {
        "total_conversations": total_conversations,
        "conversations_by_status": conversations_by_status,
        "total_messages": total_messages,
        "messages_by_sender": messages_by_sender,
        "conversations_last_24h": conversations_last_24h,
        "avg_messages_per_conversation": round(avg_messages_per_conversation, 2)
    }