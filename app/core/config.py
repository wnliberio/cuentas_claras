from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str
    
    # IA
    GEMINI_API_KEY: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()