import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database.models.client import Client

class ClientRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, client_id: uuid.UUID) -> Client | None:
        query = select(Client).where(Client.id == client_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, client: Client) -> Client:
        self.session.add(client)
        await self.session.flush()
        await self.session.refresh(client)
        return client
