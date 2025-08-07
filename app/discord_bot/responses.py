"""
Respuestas hardcodeadas para el Discord Bot

Este módulo contiene las respuestas predefinidas que el bot puede usar
antes de integrar los agentes IA.
"""

import random

# Respuestas de saludo
GREETINGS = [
    "¡Hola! 👋 Soy Ithaka Bot, tu asistente virtual.",
    "¡Hola! ¿En qué puedo ayudarte hoy?",
    "¡Saludos! Estoy aquí para responder tus preguntas.",
    "¡Hola! Bienvenido/a. ¿Cómo puedo asistirte?",
]

# Respuestas sobre el proyecto Ithaka
ITHAKA_INFO = [
    "Ithaka es un proyecto educativo innovador que utiliza IA para mejorar el aprendizaje.",
    "El proyecto Ithaka combina tecnología avanzada con pedagogía moderna.",
    "Ithaka está diseñado para proporcionar una experiencia de aprendizaje personalizada.",
]

# Respuestas técnicas básicas
TECH_RESPONSES = [
    "Este bot está construido con Python y discord.py 🐍",
    "Utilizo FastAPI como backend y PostgreSQL como base de datos.",
    "Estoy preparado para integrar agentes IA en el futuro.",
    "Mi arquitectura está basada en microservicios y tecnologías modernas.",
]

# Respuestas de ayuda
HELP_RESPONSES = [
    "Aquí están mis comandos disponibles:",
    "Puedo ayudarte con información sobre el proyecto Ithaka.",
    "Estoy en desarrollo, pero ya puedo responder algunas preguntas básicas.",
]

# Respuestas cuando no se entiende la pregunta
FALLBACK_RESPONSES = [
    "Lo siento, no entiendo esa pregunta. ¿Puedes reformularla?",
    "No estoy seguro de cómo responder a eso. ¿Puedes ser más específico?",
    "Esa pregunta está fuera de mi conocimiento actual. ¿Hay algo más en lo que pueda ayudarte?",
    "No tengo información sobre eso en este momento. ¿Te puedo ayudar con algo más?",
]

# Respuestas de despedida
GOODBYE_RESPONSES = [
    "¡Hasta luego! 👋 Que tengas un buen día.",
    "¡Adiós! Espero haberte sido útil.",
    "¡Nos vemos pronto! 😊",
    "¡Que tengas un excelente día!",
]

# FAQ hardcodeadas
FAQS = {
    "qué es ithaka": "Ithaka es un proyecto educativo que utiliza inteligencia artificial para personalizar el aprendizaje.",
    "cómo funciona": "Ithaka utiliza agentes IA para analizar las necesidades de aprendizaje y proporcionar contenido personalizado.",
    "tecnología": "Estoy construido con Python, FastAPI, PostgreSQL, y discord.py. También uso OpenAI para funcionalidades de IA.",
    "contacto": "Puedes contactar al equipo de desarrollo a través de los canales oficiales del proyecto.",
    "características": "Ofrezco respuestas inteligentes, integración con IA, y una interfaz amigable a través de Discord.",
}

def get_random_response(response_list: list) -> str:
    """Retorna una respuesta aleatoria de la lista proporcionada."""
    return random.choice(response_list)

from typing import Optional, Union

def search_faq(query: str) -> Optional[str]:
    """
    Busca en las FAQs una respuesta que coincida con la consulta.
    
    Args:
        query: La consulta del usuario
        
    Returns:
        La respuesta encontrada o None si no hay coincidencias
    """
    query_lower = query.lower()
    
    # Buscar coincidencias exactas o parciales
    for key, answer in FAQS.items():
        if key in query_lower or any(word in query_lower for word in key.split()):
            return answer
    
    return None

def get_contextual_response(message_content: str) -> str:
    """
    Genera una respuesta contextual basada en el contenido del mensaje.
    
    Args:
        message_content: El contenido del mensaje del usuario
        
    Returns:
        Una respuesta apropiada
    """
    content_lower = message_content.lower()
    
    # Patrones de saludo
    greeting_patterns = ['hola', 'hey', 'buenos días', 'buenas tardes', 'buenas noches', 'saludos']
    if any(pattern in content_lower for pattern in greeting_patterns):
        return get_random_response(GREETINGS)
    
    # Patrones de despedida
    goodbye_patterns = ['adiós', 'chao', 'hasta luego', 'nos vemos', 'bye']
    if any(pattern in content_lower for pattern in goodbye_patterns):
        return get_random_response(GOODBYE_RESPONSES)
    
    # Patrones de ayuda
    help_patterns = ['ayuda', 'help', 'qué puedes hacer', 'comandos']
    if any(pattern in content_lower for pattern in help_patterns):
        return get_random_response(HELP_RESPONSES)
    
    # Buscar en FAQs
    faq_response = search_faq(content_lower)
    if faq_response:
        return faq_response
    
    # Patrones técnicos
    tech_patterns = ['tecnología', 'cómo estás hecho', 'python', 'fastapi', 'database']
    if any(pattern in content_lower for pattern in tech_patterns):
        return get_random_response(TECH_RESPONSES)
    
    # Respuesta por defecto
    return get_random_response(FALLBACK_RESPONSES)
