import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeX Customer Support Chatbot"
    API_V1_STR: str = "/api/v1"
    
    # Postgres
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "safex_chatbot"
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # LLM & RAG
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CROSS_ENCODER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    GOOGLE_API_KEY: str = ""

    # Secrets
    SECRET_KEY: str = "CHANGE_THIS"
    N8N_WEBHOOK_SECRET: str = "CHANGE_THIS"
    WHATSAPP_CLOUD_API_SECRET: str = "CHANGE_THIS"
    WHATSAPP_VERIFY_TOKEN: str = "CHANGE_THIS"

    # n8n
    N8N_WEBHOOK_URL: str = "http://localhost:5678/webhook/"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

if not settings.SQLALCHEMY_DATABASE_URI:
    settings.SQLALCHEMY_DATABASE_URI = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
