import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.api.deps import get_db, get_current_client, get_redis
from app.services.conversation import ConversationService
from app.services.message import MessageService
from app.schemas.message import MessageResponse, MessageCreate
from shared.database.models.client import Client
from shared.common.schemas import DefaultResponse

router = APIRouter()

@router.post("/conversations/{conversation_id}/messages", response_model=DefaultResponse[MessageResponse])
async def create_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    conv_service = ConversationService(db, redis_client)
    await conv_service.get_conversation(conversation_id, current_client.id)
    
    msg_service = MessageService(db, redis_client)
    res = await msg_service.create_message(conversation_id, data.content)
    
    return DefaultResponse.success(data=MessageResponse.model_validate(res))
