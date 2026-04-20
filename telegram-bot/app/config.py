from pydantic_settings import BaseSettings
import os
from pathlib import Path


class TelegramSettings(BaseSettings):
    """Telegram Bot конфигурация"""
    
    TELEGRAM_BOT_TOKEN: str
    BACKEND_URL: str = "http://localhost:8001"
    BACKEND_API_TIMEOUT: int = 30

    class Config:
        env_file = str(Path(__file__).parent.parent.parent / ".env")
        case_sensitive = True


# Load settings
settings = TelegramSettings(
    TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
    BACKEND_URL=os.getenv("BACKEND_URL", "http://localhost:8001")
)
