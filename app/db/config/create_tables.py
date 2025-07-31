import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from ..models import Base
from .database import DATABASE_URL


async def create_tables():
    """Create database tables and enable PGVector extension"""
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Try to enable PGVector extension in its own transaction
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            print("✅ PGVector extension enabled")
    except Exception as e:
        print(f"⚠️  Could not create PGVector extension: {e}")
        print("💡 You may need to create it manually as superuser:")
        print("   CREATE EXTENSION IF NOT EXISTS vector;")
        print("✅ Continuing with table creation...")

    # Create tables in a separate transaction
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        await engine.dispose()
        raise

    await engine.dispose()
    print("✅ Database setup completed")

if __name__ == "__main__":
    asyncio.run(create_tables())
