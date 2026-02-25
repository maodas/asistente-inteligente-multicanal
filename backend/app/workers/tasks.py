import logging
from datetime import datetime, timedelta
from app.worker import celery_app
from app.services.twilio_service import send_whatsapp_message
from app.services.ai_service import generate_ai_response
from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from sqlalchemy import func

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.process_whatsapp_message")
def process_whatsapp_message(self, message_data: dict):
    """
    Procesa un mensaje de WhatsApp: guarda en BD, genera respuesta con IA y envía.
    """
    db = SessionLocal()
    try:
        from_number = message_data.get("from")
        message_body = message_data.get("body")
        
        logger.info(f"🟡 WORKER: Procesando mensaje de {from_number}: {message_body}")
        
        # 1. Buscar o crear cliente
        customer = db.query(Customer).filter(Customer.phone_number == from_number).first()
        if not customer:
            customer = Customer(phone_number=from_number)
            db.add(customer)
            db.commit()
            db.refresh(customer)
        
        # 2. Buscar conversación activa (última no terminada)
        conversation = db.query(Conversation).filter(
            Conversation.customer_id == customer.id,
            Conversation.status != ConversationStatus.ENDED
        ).order_by(Conversation.created_at.desc()).first()
        
        if not conversation:
            # Crear nueva conversación
            conversation = Conversation(
                customer_id=customer.id,
                status=ConversationStatus.BOT
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # 3. Guardar mensaje del cliente
        customer_msg = Message(
            conversation_id=conversation.id,
            sender=SenderType.CUSTOMER,
            content=message_body
        )
        db.add(customer_msg)
        db.commit()
        
        # 4. Decidir si deriva a humano (lógica simple)
        human_keywords = ["humano", "agente", "persona", "hablar con alguien", "representante"]
        needs_human = any(keyword in message_body.lower() for keyword in human_keywords)
        
        if needs_human:
            # Cambiar estado a humano
            conversation.status = ConversationStatus.HUMAN
            db.commit()
            ai_response = "Has solicitado hablar con un humano. Un agente se pondrá en contacto contigo en breve."
            sender_type = SenderType.HUMAN  # El mensaje lo enviará el sistema pero lo marcamos como humano
        else:
            # Generar respuesta con IA
            ai_response = generate_ai_response(message_body)
            sender_type = SenderType.BOT
        
        # 5. Guardar respuesta del bot/humano
        bot_msg = Message(
            conversation_id=conversation.id,
            sender=sender_type,
            content=ai_response
        )
        db.add(bot_msg)
        conversation.updated_at = func.now()
        db.commit()
        
        # 6. Enviar respuesta por WhatsApp
        result = send_whatsapp_message(from_number, ai_response)
        
        if result.get("success"):
            logger.info(f"✅ WORKER: Respuesta enviada a {from_number}")
            return {"status": "success", "to": from_number, "response": ai_response}
        else:
            logger.warning(f"⚠️ WORKER: Error enviando: {result.get('message')}")
            return {"status": "error", "to": from_number, "error": result.get('message')}
        
    except Exception as e:
        logger.error(f"🔴 WORKER ERROR: {str(e)}", exc_info=True)
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="app.workers.tasks.close_inactive_conversations")
def close_inactive_conversations():
    """
    Tarea periódica para cerrar conversaciones inactivas (sin mensajes en los últimos N minutos).
    """
    db = SessionLocal()
    try:
        # Definir tiempo de inactividad (ej: 5 minutos)
        inactive_timeout = timedelta(minutes=5)
        cutoff = datetime.utcnow() - inactive_timeout
        
        # Buscar conversaciones activas (BOT o HUMAN) cuya última actualización sea anterior al cutoff
        conversations = db.query(Conversation).filter(
            Conversation.status.in_([ConversationStatus.BOT, ConversationStatus.HUMAN]),
            Conversation.updated_at < cutoff
        ).all()
        
        closed_count = 0
        for conv in conversations:
            conv.status = ConversationStatus.ENDED
            conv.updated_at = func.now()
            closed_count += 1
        
        db.commit()
        logger.info(f"✅ Cerradas {closed_count} conversaciones inactivas")
        return closed_count
    except Exception as e:
        logger.error(f"🔴 Error cerrando conversaciones inactivas: {e}")
        db.rollback()
    finally:
        db.close()