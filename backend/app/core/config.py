from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Конфигурация приложения"""

    # App
    APP_NAME: str = "PersonalMind Pro"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # API Keys
    OPENAI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/personalmind"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Vector DB
    CHROMA_PERSIST_DIR: str = "/data/vector_db"
    CHROMA_HOST: str = "chromadb"
    CHROMA_PORT: int = 8000

    # Graph DB
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Storage
    STORAGE_MODE: str = "local"  # local или s3
    LOCAL_STORAGE_PATH: str = "/data/documents"

    # S3
    S3_ENDPOINT: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET: Optional[str] = None

    # LLM Settings (OpenAI)
    LLM_MODEL: str = "gpt-4-1106-preview"
    LLM_TEMPERATURE: float = 0.7
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Yandex GPT Settings (Alternative)
    YANDEX_API_KEY: Optional[str] = None
    YANDEX_FOLDER_ID: Optional[str] = None
    YANDEX_MODEL: str = "gpt://b1g797fquvjlp32c2ldh/yandexgpt-lite"
    
    # LLM Provider (openai or yandex)
    LLM_PROVIDER: str = "openai"

    # Memory Settings
    MAX_EPISODIC_BUFFER: int = 20
    MEMORY_CONSOLIDATION_THRESHOLD: float = 0.7
    
    # Commerce APIs
    SAMOKAT_API_KEY: Optional[str] = None
    PAPA_JOHNS_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()