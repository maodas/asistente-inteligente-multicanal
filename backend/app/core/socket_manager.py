import socketio
from typing import Dict, Any

# Crear servidor Socket.IO con CORS permitido
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode='asgi')
# Crear aplicación ASGI para montar en FastAPI
socket_app = socketio.ASGIApp(sio)

# Diccionario para mantener salas (opcional)
# Podemos usar las salas de Socket.IO directamente

async def emit_new_message(conversation_id: int, message_data: Dict[str, Any]):
    """Emitir nuevo mensaje a la sala de la conversación"""
    await sio.emit('new_message', message_data, room=f'conversation_{conversation_id}')

async def emit_conversation_updated(conversation_id: int, status: str):
    """Emitir actualización de estado a la sala de la conversación"""
    await sio.emit('conversation_updated', {'conversation_id': conversation_id, 'status': status}, room=f'conversation_{conversation_id}')