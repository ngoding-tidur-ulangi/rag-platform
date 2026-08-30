from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Chat Service"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/chat_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    RETRIEVAL_SERVICE_HOST: str = "http://localhost:8000"

settings = Settings()
