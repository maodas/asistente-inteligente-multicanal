Endpoints públicos (sin autenticación):

    POST /webhook/twilio: recibe mensajes de WhatsApp.

        Body: datos de Twilio (form-urlencoded).

        Respuesta: TwiML con mensaje de respuesta (puede ser vacío si procesamos asíncrono).

        Nota: usaremos respuesta inmediata 200 y procesaremos en background.

Endpoints para el panel (requieren JWT):

    POST /auth/login: obtiene token.

        Body: {username, password}

        Respuesta: {access_token}

    GET /conversations: lista conversaciones activas (con filtros opcionales: status, fecha).

        Query params: status, limit, offset.

        Respuesta: lista de conversaciones con último mensaje.

    GET /conversations/{id}: detalle de una conversación (todos los mensajes).

        Respuesta: conversación + array de mensajes.

    POST /conversations/{id}/take-control: cambia el estado a 'human' y asigna el agente actual.

        Body: (vacío)

        Respuesta: conversación actualizada.

    POST /conversations/{id}/messages: envía un mensaje como agente.

        Body: {content}

        Respuesta: mensaje guardado.

    GET /stats: estadísticas básicas.

        Respuesta: {total_conversations, total_messages, human_requests, ...}

Endpoints internos (para workers):

    POST /internal/send-whatsapp: enviar mensaje por Twilio (llamado por worker).

        Body: {to, body}

        Autenticación con API key interna.