from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Conversation
from app.db.config.database import get_async_session
from fastapi import HTTPException
from typing import Optional  
from datetime import datetime
from typing import List

from app.langgraph.flow import run_flow

router = APIRouter()

class ConversationCreate(BaseModel):
    email: Optional[str] = None  # Opcional  

class ConversationResponse(BaseModel):  
    id: int
    email: Optional[str]
    started_at: datetime

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
        await session.rollback()
        raise HTTPException(status_code=500, detail="Error creating conversation")

@router.get("/conversations")
async def get_conversations(
    session: AsyncSession = Depends(get_async_session)
) -> List[ConversationResponse]:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving conversations")
