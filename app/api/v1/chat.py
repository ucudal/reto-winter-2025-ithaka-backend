from fastapi import APIRouter

from app.services.chat_service import chat_service

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(message: str):
    result = await chat_service.process_message(
        user_message=message,
        user_email=None,
        conversation_id=None
    )
    return {"response": result.get("response", "Error procesando el mensaje")}
