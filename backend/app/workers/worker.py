from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks", "app.workers.timeout"]  # Añadido timeout
)

# Configuración de tareas periódicas (beat)
celery_app.conf.beat_schedule = {
    'close-inactive-conversations': {
        'task': 'app.workers.timeout.close_inactive_conversations',
        'schedule': crontab(minute='*/1'),  # Ejecutar cada minuto para pruebas (ajustar después)
    },
}

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=60,
    broker_connection_retry_on_startup=True,
)

celery = celery_app