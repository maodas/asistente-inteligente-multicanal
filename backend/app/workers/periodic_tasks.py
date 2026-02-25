import logging
from datetime import datetime, timedelta
from app.worker import celery_app
from app.core.database import SessionLocal
from app.models.conversation import Conversation, ConversationStatus
from sqlalchemy import func

logger = logging.getLogger(__name__)

@celery_app.task(name="app.workers.periodic_tasks.close_inactive_conversations")
def close_inactive_conversations():
    """
    Cierra conversaciones que han estado inactivas por más de 5 minutos.
    """
    db = SessionLocal()
    try:
        # Calcular el tiempo límite (hace 5 minutos)
        timeout_minutes = 5
        cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)
        
        # Buscar conversaciones activas (bot o human) cuya última actividad sea anterior a cutoff_time
        inactive_convs = db.query(Conversation).filter(
            Conversation.status.in_([ConversationStatus.BOT, ConversationStatus.HUMAN]),
            Conversation.last_activity_at < cutoff_time
        ).all()
        
        closed_count = 0
        for conv in inactive_convs:
            conv.status = ConversationStatus.ENDED
            conv.updated_at = func.now()
            logger.info(f"🕒 Cerrando conversación {conv.id} por inactividad")
            closed_count += 1
        
        db.commit()
        logger.info(f"✅ Tarea completada: {closed_count} conversaciones cerradas por inactividad")
        return {"closed": closed_count}
        
    except Exception as e:
        logger.error(f"🔴 Error en tarea de cierre por inactividad: {e}")
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()