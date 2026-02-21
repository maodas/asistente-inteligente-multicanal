from app.worker import celery_app

@celery_app.task
def process_whatsapp_message(message_data: dict):
    # TODO: procesar mensaje con IA y enviar respuesta
    pass