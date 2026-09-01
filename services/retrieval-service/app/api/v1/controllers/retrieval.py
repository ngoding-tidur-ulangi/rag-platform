from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.retrieval import AskRequest, AskResponse, AskStreamResponse
from app.services.retrieval_service import RetrievalService
import json

router = APIRouter()

@router.post("/ask")
async def ask_question(
    data: AskRequest,
    service: RetrievalService = Depends(deps.get_retrieval_service)
):
    async def event_generator():
        async for chunk in service.process_ask(data.conversation_id, data.question):
            yield f"data: {chunk.model_dump_json()}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
