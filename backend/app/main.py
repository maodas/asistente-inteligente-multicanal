import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from app.core.config import settings
from app.api import router

app = FastAPI(
    title="Asistente Inteligente API",
    version="0.1.0",
    description="API para asistente multicanal con IA y derivación a humano"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API del Asistente Inteligente", "docs": "/docs"}