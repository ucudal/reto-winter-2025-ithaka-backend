import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/ithaka_chatbot")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"

    # ChromaDB
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")

    # JWT
    secret_key: str = os.getenv(
        "SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Ithaka específico
    ithaka_context: str = os.getenv(
        "ITHAKA_CONTEXT",
        "Eres un asistente de postulaciones para Ithaka, el centro de emprendimiento e innovación de la UCU. "
        "Tu objetivo es ayudar a los emprendedores a completar su postulación de manera clara y completa. "
        "Mantienes un tono amigable, profesional y motivador."
    )

    class Config:
        env_file = ".env"


# Instancia global de configuración
settings = Settings()
