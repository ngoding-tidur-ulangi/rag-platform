from typing import AsyncGenerator
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import get_db as _get_db
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in _get_db():
        yield session

def get_llm_service(request: Request) -> LLMService:
    return request.app.state.llm_service

def get_retrieval_service(
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm_service)
) -> RetrievalService:
    return RetrievalService(db, llm)
