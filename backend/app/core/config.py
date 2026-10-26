from pydantic_settings import BaseSettings
from typing import Optional, List
import secrets


class Settings(BaseSettings):
    APP_NAME: str = "KAIZEN FinTech"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "kaizen-fintech-dev-secret-key-2024-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours for demo
    DATABASE_URL: str = "sqlite+aiosqlite:///./kaizen.db"
    DEMO_MODE: bool = True
    AI_PROVIDER_API_KEY: Optional[str] = None
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
