import asyncio
import os

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def test_connection():
    try:
        engine = create_async_engine(DATABASE_URL, echo=True)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("Conexión exitosa:", result.scalar())
        await engine.dispose()
    except Exception as e:
        print("Error de conexión:", e)

if __name__ == "__main__":
    asyncio.run(test_connection())
