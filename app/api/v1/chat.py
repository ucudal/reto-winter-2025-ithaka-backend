from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.chat_service import chat_service

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_email: Optional[str] = None
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    success: bool
    response: str
    conversation_id: Optional[int]
    agent_used: str
    wizard_session_id: Optional[str]
    wizard_state: str
    current_question: Optional[int]
    human_feedback_needed: bool
    metadata: dict

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_request: ChatRequest):
    """Endpoint para procesar mensajes del chat con soporte para wizard"""
    try:
        result = await chat_service.process_message(
            user_message=chat_request.message,
            user_email=chat_request.user_email,
            conversation_id=chat_request.conversation_id
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")
