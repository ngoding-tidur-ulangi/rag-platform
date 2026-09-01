import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.knowledge import Knowledge

class KnowledgeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_message_id(self, message_id: uuid.UUID) -> list[Knowledge]:
        query = select(Knowledge).where(Knowledge.message_id == message_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def create(self, knowledge: Knowledge) -> Knowledge:
        self.session.add(knowledge)
        await self.session.flush()
        await self.session.refresh(knowledge)
        return knowledge
