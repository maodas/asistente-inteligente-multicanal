from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.core.config import settings

app = FastAPI(
    title="Asistente Inteligente API",
    version="0.1.0",
    description="API para asistente multicanal con IA y derivación a humano"
)

# Configuración de CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    # Agrega aquí tu dominio de producción
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