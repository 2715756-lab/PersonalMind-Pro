from pydantic_settings import BaseSettings


class TelegramSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    BACKEND_URL: str = "http://localhost:8000"

    class Config:
        env_file = "../.env"
        case_sensitive = True


settings = TelegramSettings()
