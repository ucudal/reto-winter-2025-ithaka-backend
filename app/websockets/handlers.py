import json
import uuid
import asyncio

from fastapi import WebSocket

from .enums import AGUIEvent, Role
from .schemas import UserMessage
from ..services.chat_service import chat_service
import logging

logger = logging.getLogger(__name__)


async def emit_event(manager, websocket, action, payload):
    await manager.send_event(websocket, {"action": action, "payload": payload})


async def handle_user_message(websocket: WebSocket, message: str, manager):
    """Maneja mensajes del usuario usando el sistema completo de agentes IA"""

    try:
        data = json.loads(message)
        user_msg = UserMessage(
            id=data.get("id", str(uuid.uuid4())),
            role=Role.user,
            content=data.get("content", ""),
            name=data.get("name")
        )

        message_id = str(uuid.uuid4())
        await emit_event(manager, websocket, AGUIEvent.RUN_STARTED, {"id": message_id})

        # Procesar mensaje usando el sistema de agentes IA
        result = await chat_service.process_message(
            user_message=user_msg.content,
            user_email=data.get("email"),  # Si está disponible en el mensaje
            # Si hay ID de conversación
            conversation_id=data.get("conversation_id")
        )

        if result["success"]:
            # Enviar respuesta exitosa por chunks
            bot_response = result["response"]

            for chunk_index, chunk in enumerate(generate_chunks(bot_response)):
                await emit_event(
                    manager,
                    websocket,
                    AGUIEvent.TEXT_MESSAGE_CHUNK,
                    {
                        "id": message_id,
                        "content": chunk,
                        "chunk_index": chunk_index
                    }
                )

            # Enviar metadatos adicionales si es necesario
            metadata = {
                "conversation_id": result.get("conversation_id"),
                "agent_used": result.get("agent_used"),
                "wizard_session_id": result.get("wizard_session_id"),
                "wizard_state": result.get("wizard_state"),
                "current_question": result.get("current_question"),
                "human_feedback_needed": result.get("human_feedback_needed", False)
            }

            await emit_event(manager, websocket, AGUIEvent.RUN_FINISHED, {
                "id": message_id,
                "metadata": metadata
            })

        else:
            # Error en procesamiento
            error_message = result.get("response", "Error procesando mensaje")

            for chunk_index, chunk in enumerate(generate_chunks(error_message)):
                await emit_event(
                    manager,
                    websocket,
                    AGUIEvent.TEXT_MESSAGE_CHUNK,
                    {
                        "id": message_id,
                        "content": chunk,
                        "chunk_index": chunk_index
                    }
                )

            await emit_event(manager, websocket, AGUIEvent.RUN_ERROR, {
                "id": message_id,
                "error": result.get("error", "Error desconocido")
            })

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in message: {e}")
        await emit_event(
            manager,
            websocket,
            AGUIEvent.RUN_ERROR,
            {
                "id": str(uuid.uuid4()),
                "error": "Formato de mensaje inválido"
            }
        )
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await emit_event(
            manager,
            websocket,
            AGUIEvent.RUN_ERROR,
            {
                "id": str(uuid.uuid4()),
                "error": f"Error procesando mensaje: {str(e)}"
            }
        )


def generate_chunks(content: str):
    words = content.split()
    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
