from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.core.config import settings
from app.core.socket_manager import sio, socket_app
import socketio

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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas HTTP
app.include_router(router)

# Montar la aplicación Socket.IO en la ruta /socket.io
app.mount('/socket.io', socket_app)

# Manejadores de eventos de Socket.IO
@sio.event
async def connect(sid, environ):
    print(f"Cliente conectado: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Cliente desconectado: {sid}")

@sio.event
async def join_conversation(sid, conversation_id):
    """Unir a una sala específica para recibir mensajes de esa conversación"""
    sio.enter_room(sid, f'conversation_{conversation_id}')
    print(f"Cliente {sid} unido a conversación {conversation_id}")

@sio.event
async def leave_conversation(sid, conversation_id):
    """Salir de una sala"""
    sio.leave_room(sid, f'conversation_{conversation_id}')
    print(f"Cliente {sid} salió de conversación {conversation_id}")

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API del Asistente Inteligente", "docs": "/docs"}