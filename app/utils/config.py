from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Database credentials
    DB_USER: Optional[str] = "postgres"
    DB_PASSWORD: Optional[str] = None
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[str] = None
    DB_NAME: Optional[str] = "postgres"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings():
    return Settings()
