from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Retrieval Service"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/chat_db"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    QDRANT_HOST: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "quran"
    MODEL_NAME_OR_PATH: str = "models/BGE-M3"
    DEVICE: str = "cpu"

settings = Settings()
