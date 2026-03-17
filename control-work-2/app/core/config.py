from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import ConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Control Work"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    DATABASE_URL: Optional[str] = None
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()