import json
import uuid

from fastapi import WebSocket

from .enums import AGUIEvent, Role
from .schemas import UserMessage


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

        # aca mandarle a chat_service el mensaje para que responda la ia

        bot_content = f"Bot: You said '{user_msg.content}'"
        for chunk_index, chunk in enumerate(generate_chunks(bot_content)):
            await emit_event(
                manager,
                websocket,
                AGUIEvent.TEXT_MESSAGE_CHUNK,
                {
                    "id": message_id,
                    "role": "assistant",
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