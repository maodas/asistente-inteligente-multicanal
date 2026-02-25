from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message

router = APIRouter()

@router.get("/")
def get_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Devuelve estadísticas generales del sistema.
    """
    total_conversations = db.query(func.count(Conversation.id)).scalar()
    total_messages = db.query(func.count(Message.id)).scalar()
    human_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == ConversationStatus.HUMAN
    ).scalar()
    bot_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == ConversationStatus.BOT
    ).scalar()
    ended_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.status == ConversationStatus.ENDED
    ).scalar()
    
    # Mensajes por tipo de remitente
    customer_messages = db.query(func.count(Message.id)).filter(Message.sender == "customer").scalar()
    bot_messages = db.query(func.count(Message.id)).filter(Message.sender == "bot").scalar()
    human_messages = db.query(func.count(Message.id)).filter(Message.sender == "human").scalar()
    
    return {
        "total_conversations": total_conversations or 0,
        "total_messages": total_messages or 0,
        "conversations_by_status": {
            "bot": bot_conversations or 0,
            "human": human_conversations or 0,
            "ended": ended_conversations or 0,
        },
        "messages_by_sender": {
            "customer": customer_messages or 0,
            "bot": bot_messages or 0,
            "human": human_messages or 0,
        }
    }