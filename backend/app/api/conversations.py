from typing import List, Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.core.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from app.models.customer import Customer
from app.schemas.conversation import ConversationInDB, ConversationListItem, MessageCreate, MessageInDB
from app.services.twilio_service import send_whatsapp_message
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[ConversationListItem])
def list_conversations(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    status: Optional[ConversationStatus] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Lista conversaciones con información del último mensaje.
    """
    query = db.query(Conversation)
    if status:
        query = query.filter(Conversation.status == status)
    
    query = query.order_by(desc(Conversation.updated_at)).offset(offset).limit(limit)
    conversations = query.all()
    
    result = []
    for conv in conversations:
        last_msg = db.query(Message).filter(Message.conversation_id == conv.id).order_by(desc(Message.created_at)).first()
        customer_phone = conv.customer.phone_number if conv.customer else None
        
        result.append(ConversationListItem(
            id=conv.id,
            customer_id=conv.customer_id,
            customer_phone=customer_phone,
            status=conv.status,
            last_message=last_msg.content if last_msg else None,
            last_message_time=last_msg.created_at if last_msg else None,
            unread_count=0
        ))
    return result

@router.get("/{conversation_id}", response_model=ConversationInDB)
def get_conversation(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation

@router.post("/{conversation_id}/take-control")
def take_control(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conversation.status = ConversationStatus.HUMAN
    conversation.updated_at = func.now()
    db.commit()
    db.refresh(conversation)
    return {"message": "Control tomado", "conversation_id": conversation_id, "status": conversation.status}

@router.post("/{conversation_id}/close")
def close_conversation(
    conversation_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    conversation.status = ConversationStatus.ENDED
    conversation.updated_at = func.now()
    db.commit()
    db.refresh(conversation)
    return {"message": "Conversación cerrada", "conversation_id": conversation_id, "status": conversation.status}

@router.post("/{conversation_id}/messages", response_model=MessageInDB)
def send_message_as_agent(
    conversation_id: int,
    message: MessageCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """
    Envía un mensaje como agente humano a la conversación y lo reenvía por WhatsApp.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # Asegurar que el mensaje se envía como humano
    if message.sender != SenderType.HUMAN:
        message.sender = SenderType.HUMAN
    
    # Guardar mensaje en BD
    db_message = Message(
        conversation_id=conversation_id,
        sender=message.sender,
        content=message.content
    )
    db.add(db_message)
    conversation.updated_at = func.now()
    db.commit()
    db.refresh(db_message)
    
    # Enviar mensaje por WhatsApp al cliente
    try:
        customer = db.query(Customer).filter(Customer.id == conversation.customer_id).first()
        if customer and customer.phone_number:
            result = send_whatsapp_message(customer.phone_number, message.content)
            if not result.get("success"):
                logger.warning(f"⚠️ No se pudo enviar mensaje WhatsApp: {result.get('message')}")
                # No fallamos la petición, pero registramos
        else:
            logger.warning(f"⚠️ Cliente sin número de teléfono para conversación {conversation_id}")
    except Exception as e:
        logger.error(f"🔴 Error enviando mensaje WhatsApp: {e}", exc_info=True)
        # No interrumpimos el flujo, el mensaje ya se guardó en BD
    
    return db_message