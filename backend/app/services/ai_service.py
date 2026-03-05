import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Inicializar cliente OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ============================================
# CONFIGURACIÓN DEL NEGOCIO (personalizable)
# ============================================
BUSINESS_CONFIG = {
    "name": "ElectroTienda Guatemala",
    "hours": "Lunes a Viernes 9am-6pm, Sábados 9am-1pm",
    "phone": "+502 2345-6789",
    "email": "soporte@electrotienda.com.gt",
    "website": "www.electrotienda.com.gt",
    "returns_policy": "30 días para devoluciones con factura original",
    "warranty": "1 año en todos los productos electrónicos",
    "shipping": "Envío gratis en compras mayores a Q500 (24-48 hrs hábiles)",
    "payment_methods": "Efectivo contra entrega, tarjetas crédito/débito, transferencia",
    "categories": [
        {"name": "Teléfonos", "brands": ["Samsung", "Xiaomi", "Motorola"]},
        {"name": "Laptops", "brands": ["HP", "Lenovo", "Dell"]},
        {"name": "Accesorios", "items": ["Audífonos", "Cargadores", "Fundas"]}
    ]
}

def generate_ai_response(user_message: str) -> str:
    """
    Genera respuesta personalizada usando OpenAI con contexto del negocio
    """
    try:
        # Detectar si el usuario quiere hablar con humano
        human_keywords = ["humano", "agente", "persona", "hablar con alguien", 
                         "representante", "asesor", "queja", "reclamo"]
        if any(keyword in user_message.lower() for keyword in human_keywords):
            return ("Entiendo que prefieres hablar con un humano. "
                   f"Un agente de {BUSINESS_CONFIG['name']} te contactará "
                   "en menos de 5 minutos. Mientras tanto, ¿puedo ayudarte con algo más?")

        # Construir el prompt del sistema con toda la información del negocio
        system_prompt = f"""Eres un asistente virtual de atención al cliente para {BUSINESS_CONFIG['name']}, 
una tienda de electrónica en Guatemala.

INFORMACIÓN DEL NEGOCIO:
- Horario: {BUSINESS_CONFIG['hours']}
- Teléfono: {BUSINESS_CONFIG['phone']}
- Email: {BUSINESS_CONFIG['email']}
- Web: {BUSINESS_CONFIG['website']}
- Política de devoluciones: {BUSINESS_CONFIG['returns_policy']}
- Garantía: {BUSINESS_CONFIG['warranty']}
- Envíos: {BUSINESS_CONFIG['shipping']}
- Métodos de pago: {BUSINESS_CONFIG['payment_methods']}
- Categorías de productos: {', '.join([cat['name'] for cat in BUSINESS_CONFIG['categories']])}

DIRECTRICES:
1. Sé amable, servicial y profesional. Usa "tú" para dirigirte al cliente.
2. Responde preguntas sobre productos, precios (aproximados), disponibilidad.
3. Si no sabes algo específico (ej: precio exacto), sugiere visitar la web o contactar por teléfono.
4. Si el cliente parece frustrado o con queja, ofrécele hablar con un humano amablemente.
5. Para preguntas técnicas básicas (ej: "¿qué laptop recomiendas para estudiante?"), da recomendaciones generales basadas en las categorías disponibles.
6. Mantén respuestas concisas pero útiles (máximo 3 oraciones cuando sea posible).
7. Siempre termina ofreciendo ayuda adicional.

Ejemplos de respuestas:
- "¡Claro! En {BUSINESS_CONFIG['name']} tenemos laptops HP y Lenovo ideales para estudiantes, desde Q2,500. ¿Tienes algún presupuesto en mente?"
- "Nuestro horario es {BUSINESS_CONFIG['hours']}. ¿Necesitas ayuda con algo más?"
- "Lamento escuchar eso. Permíteme transferirte con un agente especializado que podrá resolver tu caso. ¿Me confirmas tu número de teléfono?".

RESPONDE AL SIGUIENTE MENSAJE DEL CLIENTE:
{user_message}
"""
        
        # Llamada a OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # El más económico
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content
        logger.info(f"🤖 IA (personalizada) respondió: {ai_message}")
        return ai_message
        
    except Exception as e:
        logger.error(f"❌ Error con OpenAI: {str(e)}")
        return ("Lo siento, estoy teniendo problemas para procesar tu mensaje. "
                f"Por favor llama a {BUSINESS_CONFIG['phone']} o escribe a "
                f"{BUSINESS_CONFIG['email']} para atención personalizada.")