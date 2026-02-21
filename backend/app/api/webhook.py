from fastapi import APIRouter, Request, Response
from twilio.twiml.messaging_response import MessagingResponse
import logging
from app.workers.tasks import process_whatsapp_message

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/twilio")
async def webhook_twilio(request: Request):
    try:
        form = await request.form()
        message_body = form.get("Body")
        from_number = form.get("From")
        
        logger.info(f"🔵 WEBHOOK: Mensaje recibido: '{message_body}' de {from_number}")
        
        # Verificar que la tarea existe
        logger.info(f"🔵 WEBHOOK: Intentando encolar tarea...")
        
        # Encolar tarea en Celery
        result = process_whatsapp_message.delay({
            "from": from_number,
            "body": message_body
        })
        
        logger.info(f"🔵 WEBHOOK: Tarea encolada con ID: {result.id}")
        
        # Responder inmediatamente con TwiML vacío
        resp = MessagingResponse()
        return Response(content=str(resp), media_type="application/xml")
    
    except Exception as e:
        logger.error(f"🔴 WEBHOOK ERROR: {e}", exc_info=True)
        # Incluso en error, responder con TwiML vacío
        resp = MessagingResponse()
        return Response(content=str(resp), media_type="application/xml")