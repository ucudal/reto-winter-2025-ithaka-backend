from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Conversation
from app.db.config.database import get_async_session

router = APIRouter()

class ConversationCreate(BaseModel):
    email: str = None  # Opcional

@router.post("/conversations")
async def create_conversation(
    conversation: ConversationCreate,
    session: AsyncSession = Depends(get_async_session)
):
    new_conv = Conversation(email=conversation.email)
    session.add(new_conv)
    await session.commit()
    await session.refresh(new_conv)
    return {
        "id": new_conv.id,
        "email": new_conv.email,
        "started_at": new_conv.started_at
    }

@router.get("/conversations")
async def get_conversations(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Conversation))
    conversations = result.scalars().all()
    return [
        {
            "id": c.id,
            "email": c.email,
            "started_at": c.started_at
        } for c in conversations
    ]