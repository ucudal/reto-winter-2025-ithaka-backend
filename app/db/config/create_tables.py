import asyncio
from app.db.config.database import engine, Base
from app.db.models import Conversation, Message, Postulation

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_tables())