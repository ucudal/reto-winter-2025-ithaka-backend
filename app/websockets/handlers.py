import json
import uuid

from fastapi import WebSocket

from app.services.chat_service import chat_service

from .enums import AGUIEvent, Role
from .schemas import UserMessage

# Error messages
ERROR_MESSAGES = {
    "PROCESSING_ERROR": "Error procesando el mensaje"
}


async def emit_event(manager, websocket, action, payload):
    await manager.send_event(websocket, {"action": action, "payload": payload})


async def handle_user_message(websocket: WebSocket, message: str, manager):
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

        # TODO: Implement conversation tracking per WebSocket connection
        # For now, using None for both user_email and conversation_id
        result = await chat_service.process_message(
            user_message=user_msg.content,
            user_email=None,
            conversation_id=None
        )
        grafo_response = result.get(
            "response", ERROR_MESSAGES["PROCESSING_ERROR"])

        for chunk_index, chunk in enumerate(generate_chunks(grafo_response)):
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

        await emit_event(manager, websocket, AGUIEvent.RUN_FINISHED, {"id": message_id})
    except Exception as e:
        await emit_event(
            manager,
            websocket,
            AGUIEvent.RUN_ERROR,
            {
                "id": str(uuid.uuid4()),
                "error": f"Error processing message: {str(e)}"
            }
        )


def generate_chunks(content: str):
    words = content.split()
    for i, word in enumerate(words):
        if i < len(words) - 1:
            yield word + " "
        else:
            yield word
