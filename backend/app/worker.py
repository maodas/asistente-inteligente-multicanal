from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]  # Esta línea es CRUCIAL
)

celery_app.conf.task_routes = {
    "app.workers.tasks.*": {"queue": "default"}
}

# Opcional: eliminar el warning
celery_app.conf.broker_connection_retry_on_startup = True