import json

from .schemas import ChatMessage


async def handle_user_message(websocket, manager, message: str):
    try:
        data = json.loads(message)
        user_msg = ChatMessage(**data)

        # aca agregar llamada a chat_service para que responda la ia

        bot_response = ChatMessage(
            message=f"Bot: You said '{user_msg.message}'",
            sender="bot",
            type="text"
        )

        await manager.send_message(bot_response.json(), websocket)

    except Exception as e:
        error_msg = ChatMessage(
            message=f"Error processing message: {str(e)}",
            sender="bot",
            type="error"
        )
        await manager.send_message(error_msg.model_dump_json(), websocket)

    finally:
        manager.disconnect(websocket)
