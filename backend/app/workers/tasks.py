import logging
import httpx
import asyncio
from app.core.config import settings
from app.worker import celery_app
from app.services.twilio_service import send_whatsapp_message
from app.services.ai_service import generate_ai_response
from app.core.socket_manager import emit_new_message, emit_conversation_updated


logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="app.workers.tasks.process_whatsapp_message")
def process_whatsapp_message(self, message_data: dict):
    """
    Procesa un mensaje de WhatsApp: genera respuesta con IA y envía
    """
    try:
        from_number = message_data.get("from")
        message_body = message_data.get("body")
        
        logger.info(f"🟡 WORKER: Procesando mensaje de {from_number}: {message_body}")

                # Después de guardar customer_msg
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://backend:8000/internal/notify-message",  # dentro de docker, el host es 'backend'
                    json={
                        "conversation_id": conversation.id,
                        "message_data": {
                            "id": customer_msg.id,
                            "sender": customer_msg.sender,
                            "content": customer_msg.content,
                            "created_at": customer_msg.created_at.isoformat()
                        }
                    },
                    timeout=2.0
                )
        except Exception as e:
            logger.error(f"Error notificando mensaje: {e}")
        
        # Generar respuesta con IA
        ai_response = generate_ai_response(message_body)
        logger.info(f"🟡 WORKER: Respuesta generada: {ai_response}")
                # Después de guardar customer_msg
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"http://backend:8000/internal/notify-message",  # dentro de docker, el host es 'backend'
                    json={
                        "conversation_id": conversation.id,
                        "message_data": {
                            "id": customer_msg.id,
                            "sender": customer_msg.sender,
                            "content": customer_msg.content,
                            "created_at": customer_msg.created_at.isoformat()
                        }
                    },
                    timeout=2.0
                )
        except Exception as e:
            logger.error(f"Error notificando mensaje: {e}")
        
        # Enviar respuesta por WhatsApp
        result = send_whatsapp_message(from_number, ai_response)
        
        if result.get("success"):
            logger.info(f"✅ WORKER: Respuesta enviada a {from_number}")
            return {"status": "success", "to": from_number, "response": ai_response}
        else:
            # Si hay error de límite, registrar pero no reintentar
            if result.get("error") == "daily_limit":
                logger.warning(f"⚠️ WORKER: Límite diario alcanzado para {from_number}")
                return {
                    "status": "limit_reached", 
                    "to": from_number, 
                    "response": ai_response,
                    "error": "daily_limit"
                }
            else:
                # Para otros errores, reintentar
                logger.error(f"🔴 WORKER ERROR: {result.get('message')}")
                raise self.retry(exc=Exception(result.get('message')), countdown=60, max_retries=3)
        
    except Exception as e:
        logger.error(f"🔴 WORKER ERROR: {str(e)}", exc_info=True)
        # En caso de error, no reintentar automáticamente para no gastar límite
        return {
            "status": "error",
            "to": from_number,
            "error": str(e)
        }
