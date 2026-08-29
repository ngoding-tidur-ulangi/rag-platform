from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.retrieval import AskRequest, AskResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db: AsyncSession = Depends(deps.get_db)
):
    service = RetrievalService(db)
    return await service.process_ask(request.question)
