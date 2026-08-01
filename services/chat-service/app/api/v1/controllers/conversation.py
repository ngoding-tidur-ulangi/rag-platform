import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.api.deps import get_db, get_current_client, get_redis
from app.services.conversation import ConversationService
from app.schemas.conversation import (
    ConversationResponse, 
    ConversationCreate, 
    ConversationUpdateTitle
)
from shared.database.models.client import Client
from shared.common.schemas import DefaultResponse

router = APIRouter()

@router.get("conversation", response_model=DefaultResponse[list[ConversationResponse]])
async def get_conversations(
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    service = ConversationService(db, redis_client)
    res = await service.get_conversation_list(current_client.id)
    return DefaultResponse(data=res)

@router.get("conversation/{conversation_id}", response_model=DefaultResponse[dict])
async def get_conversation_detail(
    conversation_id: uuid.UUID,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    service = ConversationService(db, redis_client)
    res = await service.get_conversation_detail(conversation_id, current_client.id)
    return DefaultResponse(data=res)

@router.post("conversation", response_model=DefaultResponse[ConversationResponse])
async def create_conversation(
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    service = ConversationService(db, redis_client)
    res = await service.create_conversation(current_client.id)
    return DefaultResponse(data=res)

@router.patch("conversation/{conversation_id}/title", response_model=DefaultResponse[ConversationResponse])
async def update_conversation_title(
    conversation_id: uuid.UUID,
    data: ConversationUpdateTitle,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    service = ConversationService(db, redis_client)
    res = await service.update_conversation_title(conversation_id, current_client.id, data.title)
    return DefaultResponse(data=res)

@router.delete("conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    service = ConversationService(db, redis_client)
    await service.delete_conversation(conversation_id, current_client.id)
    return DefaultResponse(data=None)
