from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.config.database import get_async_session
from app.db.models import Conversation
from app.services.chat_service import chat_service

router = APIRouter()

class ConversationCreate(BaseModel):
    email: Optional[str] = None  # Opcional  

class ConversationResponse(BaseModel):  
    id: int
    email: Optional[str]
    started_at: datetime

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
        raise e
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    session: AsyncSession = Depends(get_async_session)
) -> ConversationResponse:
    try:
        new_conv = Conversation(email=conversation.email)
        session.add(new_conv)
        await session.commit()
        await session.refresh(new_conv)
        return ConversationResponse(
            id=new_conv.id,
            email=new_conv.email,
            started_at=new_conv.started_at
        )
    except Exception as e:
        raise e
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error creating conversation")

@router.get("/conversations")
async def get_conversations(
    session: AsyncSession = Depends(get_async_session)
) -> list[ConversationResponse]:
    try:
        result = await session.execute(select(Conversation))
        conversations = result.scalars().all()
        return [
            ConversationResponse(
                id=c.id,
                email=c.email,
                started_at=c.started_at
            ) for c in conversations
        ]
    except Exception:
        raise e
        raise HTTPException(status_code=500, detail="Error retrieving conversations")
