import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.conversation import Conversation

class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_client_id(self, client_id: uuid.UUID) -> List[Conversation]:
        query = (
            select(Conversation)
            .where(Conversation.client_id == client_id)
            .order_by(Conversation.last_message_at.desc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, conversation_id: uuid.UUID) -> Conversation | None:
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def update(self, conversation: Conversation) -> Conversation:
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def delete(self, conversation: Conversation) -> None:
        await self.session.delete(conversation)
        await self.session.flush()
    
