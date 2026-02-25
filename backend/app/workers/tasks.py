import logging
from app.worker import celery_app
from app.services.twilio_service import send_whatsapp_message
from app.services.ai_service import generate_ai_response
from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, SenderType
from sqlalchemy import func  # <--- IMPORTANTE: importar func
import httpx

logger = logging.getLogger(__name__)

# URL del backend interno para notificaciones (usando el nombre del contenedor)
INTERNAL_API_URL = "http://backend:8000/internal"

def notify_new_message(conversation_id: int, message_data: dict):
    """
    Notifica al backend (vía API interna) que hay un nuevo mensaje,
    para que pueda enviarlo por WebSocket a los clientes.
    """
    try:
        with httpx.Client() as client:
            response = client.post(
                f"{INTERNAL_API_URL}/conversations/{conversation_id}/messages/notify",
                json=message_data,
                timeout=5.0
            )
            response.raise_for_status()
            logger.info(f"📡 Notificación enviada para conversación {conversation_id}")
    except Exception as e:
        logger.error(f"⚠️ Error notificando nuevo mensaje: {e}")

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
        
        # Notificar al frontend (WebSocket) sobre el nuevo mensaje
        notify_new_message(conversation.id, {
            "id": customer_msg.id,
            "conversation_id": conversation.id,
            "sender": "customer",
            "content": message_body,
            "created_at": customer_msg.created_at.isoformat()
        })
        
        # 4. Decidir si deriva a humano (lógica simple)
        human_keywords = ["humano", "agente", "persona", "hablar con alguien", "representante", "asesor"]
        needs_human = any(keyword in message_body.lower() for keyword in human_keywords)
        
        if needs_human:
            # Cambiar estado a humano
            conversation.status = ConversationStatus.HUMAN
            db.commit()
            ai_response = "Has solicitado hablar con un humano. Un agente se pondrá en contacto contigo en breve."
            sender_type = SenderType.HUMAN
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
        
        # No es necesario asignar updated_at manualmente porque el modelo tiene onupdate
        # Pero si quieres forzar la actualización, usa func.now() correctamente:
        # conversation.updated_at = func.now()
        
        db.commit()
        db.refresh(bot_msg)
        
        # Notificar al frontend sobre la respuesta
        notify_new_message(conversation.id, {
            "id": bot_msg.id,
            "conversation_id": conversation.id,
            "sender": sender_type.value,
            "content": ai_response,
            "created_at": bot_msg.created_at.isoformat()
        })
        
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
        # Opcional: reintentar
        # raise self.retry(exc=e, countdown=60, max_retries=3)
        return {"status": "error", "error": str(e)}
    finally:
        db.close()