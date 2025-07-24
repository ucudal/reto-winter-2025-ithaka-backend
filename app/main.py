from app.api.v1.websockets import router as websockets_router
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Conversation
from app.db.config.database import get_async_session
from pydantic import BaseModel

app = FastAPI(title="Chatbot Backend", version="1.0.0")

app.include_router(websockets_router, prefix="/api/v1/websockets", tags=["Websockets"])

@app.get("/")
def root():
    return {"message": "API está corriendo"}

# Esquema de entrada para crear una conversación
class ConversationCreate(BaseModel):
    email: str = None  # Opcional

@app.post("/conversations")
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
    
@app.get("/conversations")
async def get_conversations(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Conversation))
    conversations = result.scalars().all()
    # Puedes convertir a dict si quieres, aquí solo devuelvo los objetos
    return [ 
        {
            "id": c.id,
            "email": c.email,
            "started_at": c.started_at
        } for c in conversations
    ]
    
    
