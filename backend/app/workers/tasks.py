from app.worker import celery_app
from twilio.rest import Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

@celery_app.task
def process_whatsapp_message(message_data: dict):
    """
    Tarea asíncrona que procesa un mensaje de WhatsApp y envía una respuesta.
    """
    logger.info("🟢 WORKER: Tarea iniciada!")
    logger.info(f"🟢 WORKER: Datos recibidos: {message_data}")
    
    from_number = message_data.get("from")
    body = message_data.get("body")
    
    logger.info(f"🟢 WORKER: Procesando mensaje: '{body}' de {from_number}")
    
    # Inicializar cliente de Twilio
    try:
        logger.info("🟢 WORKER: Inicializando cliente Twilio")
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Enviar respuesta (por ahora un eco simple)
        response_text = f"Recibí tu mensaje: '{body}'. (Pronto con IA)"
        logger.info(f"🟢 WORKER: Enviando respuesta: {response_text}")
        
        message = client.messages.create(
            body=response_text,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=from_number
        )
        logger.info(f"🟢 WORKER: Respuesta enviada, SID: {message.sid}")
        
    except Exception as e:
        logger.error(f"🔴 WORKER ERROR: {e}", exc_info=True)