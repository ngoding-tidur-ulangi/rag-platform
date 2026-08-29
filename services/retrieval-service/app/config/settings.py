from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Retrieval Service"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/chat_db"
    GEMINI_API_KEY: str = ""

settings = Settings()
