from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # Database credentials
    DB_USER: Optional[str] = Field(alias="user", default="postgres")
    DB_PASSWORD: Optional[str] = Field(alias="password", default=None)
    DB_HOST: Optional[str] = Field(alias="host", default=None)
    DB_PORT: Optional[str] = Field(alias="port", default=None)
    DB_NAME: Optional[str] = Field(alias="dbname", default="postgres")

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings():
    return Settings()
