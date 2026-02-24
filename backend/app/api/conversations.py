from typing import Optional, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
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

@router.post("/{conversation_id}/messages", response_model=MessageInDB)
def send_message_as_agent(
    conversation_id: int,
    message: MessageCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    # 1. Obtener la conversación
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    
    # 2. Verificar que el cliente tenga número de teléfono (para WhatsApp)
    if not conversation.customer or not conversation.customer.phone_number:
        raise HTTPException(
            status_code=400, 
            detail="El cliente no tiene un número de WhatsApp asociado"
        )
    
    # 3. Crear el mensaje en BD
    db_message = Message(
        conversation_id=conversation_id,
        sender=SenderType.HUMAN,
        content=message.content
    )
    db.add(db_message)
    conversation.updated_at = func.now()
    db.commit()
    db.refresh(db_message)
    
    # 4. Enviar el mensaje por WhatsApp usando Twilio
    try:
        twilio_result = send_whatsapp_message(
            to=conversation.customer.phone_number,
            body=message.content
        )
        if not twilio_result.get("success"):
            logger.warning(f"El mensaje se guardó pero no se pudo enviar por WhatsApp: {twilio_result.get('message')}")
            # No lanzamos excepción porque el mensaje ya está guardado, pero podrías notificar al frontend si quieres
    except Exception as e:
        logger.error(f"Error enviando mensaje por Twilio: {e}", exc_info=True)
        # El mensaje ya está guardado, no interrumpimos la respuesta
    
    return db_message