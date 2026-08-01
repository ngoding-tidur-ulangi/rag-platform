import uuid
from typing import List
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_client
from app.services.conversation import ConversationService
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationResponse, 
    ConversationCreate, 
    ConversationUpdateTitle
)
from app.schemas.message import MessageResponse
from shared.database.models.client import Client
from shared.common.schemas import DefaultResponse

router = APIRouter()

@router.get("conversations", response_model=DefaultResponse[List[ConversationResponse]])
async def list_conversations(
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    res = await service.get_conversation_list(current_client.id)
    return DefaultResponse(data=res)

@router.post("conversations", response_model=DefaultResponse[ConversationResponse])
async def create_conversation(
    data: ConversationCreate,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    res = await service.create_conversation(current_client.id)
    return DefaultResponse(data=res)

@router.get("conversations/{conversation_id}", response_model=DefaultResponse[dict])
async def get_conversation(
    conversation_id: uuid.UUID,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    conversation = await service.get_conversation(conversation_id, current_client.id)
    
    # Get messages
    msg_repo = MessageRepository(db)
    messages = await msg_repo.get_by_conversation_id(conversation_id)
    
    return DefaultResponse(data={
        "conversation": ConversationResponse.model_validate(conversation),
        "messages": [MessageResponse.model_validate(m) for m in messages]
    })

@router.patch("conversations/{conversation_id}", response_model=DefaultResponse[ConversationResponse])
async def rename_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdateTitle,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    res = await service.update_conversation_title(conversation_id, current_client.id, data.title)
    return DefaultResponse(data=res)

@router.delete("conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_client: Client = Depends(get_current_client),
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)
    await service.delete_conversation(conversation_id, current_client.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
