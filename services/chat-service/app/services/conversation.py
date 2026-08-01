import uuid
import json
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import ConversationResponse
from app.schemas.message import MessageResponse
from shared.database.models.conversation import Conversation
from shared.common.exceptions import NotFoundException

class ConversationService:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis = None):
        self.session = session
        self.repository = ConversationRepository(session)
        self.message_repository = MessageRepository(session)
        self.redis = redis_client

    async def _invalidate_client_cache(self, client_id: uuid.UUID):
        if self.redis:
            await self.redis.delete(f"client:{client_id}:conversations")

    async def _invalidate_conversation_cache(self, conversation_id: uuid.UUID):
        if self.redis:
            await self.redis.delete(f"conversation:{conversation_id}")

    async def get_conversation_list(self, client_id: uuid.UUID) -> List[ConversationResponse]:
        cache_key = f"client:{client_id}:conversations"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                data = json.loads(cached)
                return [ConversationResponse.model_validate(c) for c in data]

        conversations = await self.repository.get_by_client_id(client_id)
        res = [ConversationResponse.model_validate(c) for c in conversations]
        
        if self.redis:
            await self.redis.setex(
                cache_key,
                600,  # 10 minutes
                json.dumps([c.model_dump(mode='json') for c in res])
            )
        return res

    async def get_conversation_detail(self, conversation_id: uuid.UUID, client_id: uuid.UUID) -> dict:
        cache_key = f"conversation:{conversation_id}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)

        conversation = await self.repository.get_by_id(conversation_id)
        if not conversation or conversation.client_id != client_id:
            raise NotFoundException(f"Conversation with id {conversation_id} not found")
        
        messages = await self.message_repository.get_by_conversation_id(conversation_id)
        
        res = {
            "conversation": ConversationResponse.model_validate(conversation).model_dump(mode='json'),
            "messages": [MessageResponse.model_validate(m).model_dump(mode='json') for m in messages]
        }
        
        if self.redis:
            await self.redis.setex(cache_key, 600, json.dumps(res))
            
        return res

    async def get_conversation(self, conversation_id: uuid.UUID, client_id: uuid.UUID) -> Conversation:
        conversation = await self.repository.get_by_id(conversation_id)
        if not conversation or conversation.client_id != client_id:
            raise NotFoundException(f"Conversation with id {conversation_id} not found")
        return conversation

    async def create_conversation(self, client_id: uuid.UUID) -> ConversationResponse:
        random_title = f"Conversation-{uuid.uuid4().hex[:8]}"
        conversation = Conversation(
            client_id=client_id,
            title=random_title
        )
        created = await self.repository.create(conversation)
        await self.session.commit()
        
        await self._invalidate_client_cache(client_id)
        
        return ConversationResponse.model_validate(created)

    async def update_conversation_title(self, conversation_id: uuid.UUID, client_id: uuid.UUID, title: str) -> ConversationResponse:
        conversation = await self.get_conversation(conversation_id, client_id)
        
        conversation.title = title
        updated = await self.repository.update(conversation)
        await self.session.commit()
        
        await self._invalidate_client_cache(client_id)
        await self._invalidate_conversation_cache(conversation_id)
        
        return ConversationResponse.model_validate(updated)

    async def delete_conversation(self, conversation_id: uuid.UUID, client_id: uuid.UUID) -> None:
        conversation = await self.get_conversation(conversation_id, client_id)
        await self.repository.delete(conversation)
        await self.session.commit()
        
        await self._invalidate_client_cache(client_id)
        await self._invalidate_conversation_cache(conversation_id)

    async def update_last_message_at(self, conversation_id: uuid.UUID, last_message_at: datetime) -> ConversationResponse:
        conversation = await self.repository.get_by_id(conversation_id)
        if not conversation:
            raise NotFoundException(f"Conversation with id {conversation_id} not found")
        
        conversation.last_message_at = last_message_at
        updated = await self.repository.update(conversation)
        await self.session.commit()
        
        await self._invalidate_client_cache(conversation.client_id)
        await self._invalidate_conversation_cache(conversation_id)
        
        return ConversationResponse.model_validate(updated)
