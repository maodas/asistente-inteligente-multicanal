import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Inicializar cliente OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_ai_response(user_message: str) -> str:
    """
    Genera una respuesta usando OpenAI
    """
    try:
        # Prompt base para el asistente
        system_prompt = """Eres un asistente de atención al cliente amable y servicial. 
        Respondes preguntas de manera concisa y clara. Si el usuario pide hablar con un humano, 
        debes indicar que lo transferirás con un agente."""
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # El más económico
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        ai_message = response.choices[0].message.content
        logger.info(f"🤖 IA respondió: {ai_message}")
        return ai_message
        
    except Exception as e:
        logger.error(f"❌ Error con OpenAI: {str(e)}")
        # Fallback en caso de error con la IA
        return "Lo siento, estoy teniendo problemas para procesar tu mensaje. Un agente te contactará pronto."