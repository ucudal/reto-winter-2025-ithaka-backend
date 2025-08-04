"""
Endpoint para integración con CopilotKit
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CopilotKitRequest(BaseModel):
    """Modelo para las peticiones de CopilotKit"""
    message: str
    conversation_id: Optional[int] = None
    user_email: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class CopilotKitResponse(BaseModel):
    """Modelo para las respuestas de CopilotKit"""
    response: str
    agent_used: Optional[str] = None
    conversation_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


def get_mock_faq_response(user_message: str) -> str:
    """Simula respuestas del agente de FAQ para pruebas"""
    message_lower = user_message.lower()

    # Respuestas simuladas basadas en palabras clave
    if "fellows" in message_lower or "fellows" in message_lower:
        return """El programa Fellows es una beca completa creada por la universidad de Stanford y dictada por la universidad de Twente. Te ayuda a desarrollar habilidades intraemprendedoras en tu experiencia universitaria. 

Desde UCU-Ithaka seleccionamos y becamos 4 estudiantes para que se conviertan en agentes de cambio. Los seleccionados tienen la posibilidad de asistir al evento internacional de meetup de fellows en la universidad de Twente, Países Bajos durante 3 días (los pasajes son costeados por la UCU).

Más información: https://programa-university-inno-k2jjjij.gamma.site/"""

    elif "costo" in message_lower or "precio" in message_lower or "gratis" in message_lower or "pagar" in message_lower:
        return """¡Todas nuestras actividades son completamente gratuitas! 

En Ithaka creemos que el emprendimiento debe ser accesible para todos. Nuestros cursos, mentorías, programas y actividades de incubadora no tienen costo. Solo necesitas ganas de aprender y emprender.

Para estudiantes UCU solo se requieren créditos disponibles para cursos electivos."""

    elif "curso" in message_lower or "electivo" in message_lower:
        return """Tenemos un PDF con todos los cursos electivos: https://bit.ly/ElectivasIthaka

Si te interesa el paquete completo de cursos puedes dirigirte al minor de innovación y emprendimiento: https://minor-innovacion-emprend-6ucsomp.gamma.site/

Ofrecemos múltiples cursos y capacitaciones en emprendimiento e innovación. Todos nuestros cursos son gratuitos para la comunidad UCU."""

    elif "convocatoria" in message_lower or "novedad" in message_lower or "evento" in message_lower:
        return """Puedes seguirnos en nuestras redes sociales (Instagram, Twitter y LinkedIn) o suscribirte a nuestro newsletter. 

Allí publicamos todas las convocatorias, eventos, y oportunidades disponibles. Así no te pierdes ninguna oportunidad de crecimiento emprendedor."""

    elif "ithaka" in message_lower or "centro" in message_lower:
        return """Ithaka es el centro de emprendimiento e innovación de la Universidad Católica del Uruguay. 

Ofrecemos programas educativos, incubadora de startups, mentorías, y capacitaciones para desarrollar el espíritu emprendedor. Estamos abiertos tanto a la comunidad UCU como a emprendedores externos."""

    else:
        return """¡Hola! Soy el asistente de ITHAKA, el centro de emprendimiento e innovación de la UCU.

Puedo ayudarte con información sobre:
• Programa Fellows
• Cursos electivos y capacitaciones
• Costos de nuestros servicios (¡todo es gratuito!)
• Convocatorias y eventos
• Información general sobre ITHAKA

¿En qué puedo ayudarte específicamente?"""


@router.post("/copilotkit")
async def copilotkit_endpoint(request: CopilotKitRequest):
    """
    Endpoint para CopilotKit que procesa mensajes usando el agente de FAQ
    """
    try:
        logger.info(
            f"🔄 Procesando mensaje CopilotKit: {request.message[:50]}...")
        logger.info(f"📝 Request completo: {request}")

        # Simular respuesta del agente de FAQ
        response = get_mock_faq_response(request.message)

        logger.info(
            f"✅ Respuesta generada exitosamente para: {request.message[:50]}...")
        logger.info(f"📤 Enviando respuesta: {response[:100]}...")

        result = CopilotKitResponse(
            response=response,
            agent_used="faq",
            conversation_id=request.conversation_id or 1,
            metadata={
                "next_action": "send_response",
                "faq_results": [],
                "validation_results": None
            }
        )

        logger.info(f"🎉 Respuesta enviada exitosamente")
        return result

    except Exception as e:
        logger.error(f"❌ Error en endpoint CopilotKit: {e}")
        logger.error(f"📋 Request que causó el error: {request}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.post("/copilotkit/agents/execute")
async def copilotkit_agents_execute(request: dict):
    """
    Endpoint para ejecutar agentes específicos de CopilotKit
    """
    try:
        # Extraer información del request
        agent_name = request.get("agent", "faq")
        logger.info(f"🔄 Procesando agente: {agent_name}")
        message = request.get("message", "")

        # Procesar con el agente correspondiente
        if agent_name == "faq":
            response = get_mock_faq_response(message)
        else:
            response = "Lo siento, no puedo procesar esa solicitud en este momento."

        return {
            "response": response,
            "agent_used": agent_name,
            "success": True
        }

    except Exception as e:
        logger.error(f"Error en endpoint de agentes: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )


@router.post("/copilotkit/actions")
async def copilotkit_actions():
    """
    Endpoint para obtener acciones disponibles
    """
    return {
        "actions": []
    }


@router.post("/copilotkit/agents")
async def copilotkit_agents():
    """
    Endpoint para obtener agentes disponibles
    """
    return {
        "agents": [
            {
                "name": "faq",
                "description": "Agente de FAQ para responder preguntas sobre ITHAKA",
                "assistantId": "ithaka-faq-agent"
            }
        ]
    }


@router.get("/copilotkit/health")
async def copilotkit_health():
    """Health check para CopilotKit"""
    return {"status": "healthy", "service": "copilotkit-endpoint"}


@router.get("/copilotkit/info")
@router.post("/copilotkit/info")
async def copilotkit_info():
    """Endpoint de información para CopilotKit"""
    return {
        "agents": [
            {
                "name": "faq",
                "description": "Agente de FAQ para responder preguntas sobre ITHAKA",
                "assistantId": "ithaka-faq-agent"
            }
        ],
        "actions": [],
        "remoteEndpoints": []
    }
