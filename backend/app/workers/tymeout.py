import logging
from datetime import datetime, timedelta
from celery import Celery
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.conversation import Conversation, ConversationStatus
from app.worker import celery_app

logger = logging.getLogger(__name__)

@celery_app.task(name="app.workers.timeout.close_inactive_conversations")
def close_inactive_conversations():
    """
    Tarea periódica que cierra conversaciones inactivas después de X minutos.
    """
    db: Session = SessionLocal()
    try:
        # Definir tiempo de inactividad (5 minutos)
        inactivity_limit = datetime.utcnow() - timedelta(minutes=5)
        
        # Buscar conversaciones activas (BOT o HUMAN) con last_activity_at anterior al límite
        inactive_convs = db.query(Conversation).filter(
            Conversation.status.in_([ConversationStatus.BOT, ConversationStatus.HUMAN]),
            Conversation.last_activity_at < inactivity_limit
        ).all()
        
        for conv in inactive_convs:
            logger.info(f"Cerrando conversación {conv.id} por inactividad (última actividad: {conv.last_activity_at})")
            conv.status = ConversationStatus.ENDED
            conv.updated_at = datetime.utcnow()
        
        db.commit()
        logger.info(f"Tarea de timeout completada: {len(inactive_convs)} conversaciones cerradas.")
    except Exception as e:
        logger.error(f"Error en tarea de timeout: {e}")
        db.rollback()
    finally:
        db.close()