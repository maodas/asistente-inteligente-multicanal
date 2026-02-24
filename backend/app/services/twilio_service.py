# app/services/twilio_service.py
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from app.core.config import settings

logger = logging.getLogger(__name__)

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to: str, body: str) -> dict:
    try:
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=to
        )
        logger.info(f"✅ Mensaje enviado a {to}, SID: {message.sid}")
        return {"success": True, "sid": message.sid}
    except TwilioRestException as e:
        logger.error(f"❌ Error de Twilio: {e}")
        return {"success": False, "error": "twilio_error", "message": str(e)}
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return {"success": False, "error": "unexpected", "message": str(e)}