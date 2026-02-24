import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <--- ESTA LÍNEA FALTABA
from app.core.config import settings
from app.api import router

app = FastAPI(
    title="Asistente Inteligente API",
    version="0.1.0",
    description="API para asistente multicanal con IA y derivación a humano"
)

origins = [
    "http://localhost:5173",      # Vite por defecto
    "http://127.0.0.1:5173",
    "http://localhost:3000",      # Por si acaso (React sin Vite)
    # Agrega aquí tu dominio de producción cuando lo tengas
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API del Asistente Inteligente", "docs": "/docs"}