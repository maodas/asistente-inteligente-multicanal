
### Guía de despliegue en Render

Crear `docs/GUIA_DESPLIEGUE.md` con pasos para desplegar backend, frontend, y configurar servicios. Incluir:

- Crear base de datos PostgreSQL en Render.
- Crear servicio web para el backend (FastAPI) con Docker.
- Crear servicio web para el frontend (estático) o también con Docker.
- Configurar variables de entorno.
- Configurar el worker como servicio separado (background worker) en Render.
- Configurar Redis (usar Redis Cloud o Redis de Render).
- Actualizar webhook de Twilio con la URL del backend desplegado.

### Capturas de pantalla

Tomar capturas de:
- Pantalla de login
- Dashboard con conversaciones
- Detalle de conversación (modo bot y modo humano)
- (Opcional) Estadísticas

Guardar en `docs/images/` y referenciarlas en el README.

---

## 📌 Resumen de tareas a realizar

1. **WebSockets**:
   - [ ] Instalar `python-socketio` en backend.
   - [ ] Crear `socket_manager.py` y montarlo en main.py.
   - [ ] Modificar worker para emitir eventos.
   - [ ] Instalar `socket.io-client` en frontend.
   - [ ] Crear servicio de socket y hooks.
   - [ ] Actualizar Dashboard y ConversationDetail para tiempo real.

2. **Pruebas automatizadas**:
   - [ ] Instalar pytest y dependencias.
   - [ ] Crear `conftest.py` y pruebas básicas.
   - [ ] Añadir pruebas de autenticación, conversaciones y worker.

3. **Documentación**:
   - [ ] Crear README.md con badges, capturas, instrucciones.
   - [ ] Crear `docs/GUIA_DESPLIEGUE.md`.
   - [ ] Tomar capturas de pantalla y guardarlas.

¿Quieres que empecemos con WebSockets ahora mismo? Podemos ir paso a paso y voy generando el código completo para cada archivo.