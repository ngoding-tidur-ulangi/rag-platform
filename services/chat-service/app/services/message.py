import uuid
import logging
import httpx
import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.repositories.message import MessageRepository
from app.repositories.conversation import ConversationRepository
from shared.database.models.message import Message, MessageRole
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MessageService:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis = None):
        self.session = session
        self.repository = MessageRepository(session)
        self.conversation_repository = ConversationRepository(session)
        self.redis = redis_client

    async def create_message(self, conversation_id: uuid.UUID, content: str, role: str = "USER"):
        logger.info(f"Creating message for conversation: {conversation_id}, role: {role}")
        message = Message(
            conversation_id=conversation_id,
            content=content,
            role=MessageRole(role.upper())
        )
        created = await self.repository.create(message)
        
        # Update conversation last_message_at
        conversation = await self.conversation_repository.get_by_id(conversation_id)
        if conversation:
            conversation.last_message_at = created.created_at
            await self.conversation_repository.update(conversation)
            
        await self.session.commit()
        
        # Invalidate cache
        if self.redis:
            logger.info(f"Invalidating caches for conversation: {conversation_id}")
            await self.redis.delete(f"conversation:{conversation_id}")
            if conversation:
                await self.redis.delete(f"client:{conversation.client_id}:conversations")

    async def stream_chat_response(self, conversation_id: uuid.UUID, content: str) -> AsyncGenerator[str, None]:
        # 1. Create user message
        await self.create_message(conversation_id, content, role="USER")

        # 2. Call retrieval-service
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{settings.RETRIEVAL_SERVICE_HOST}/api/v1/ask",
                json={
                    "question": content,
                    "conversation_id": str(conversation_id)
                }
            ) as response:
                if response.status_code != 200:
                    error_detail = await response.aread()
                    logger.error(f"Error from retrieval-service: {response.status_code} - {error_detail}")
                    yield f"data: {json.dumps({'error': 'Failed to get response from retrieval service'})}\n\n"
                    return

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        yield f"{line}\n\n"
