import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.message import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_conversation_id(self, conversation_id: uuid.UUID) -> list[Message]:
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message
