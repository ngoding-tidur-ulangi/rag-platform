import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.client import ClientRepository
from shared.database.models.client import Client

class ClientService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ClientRepository(session)

    async def get_or_create_client(self, client_id: uuid.UUID) -> Client:
        client = await self.repository.get_by_id(client_id)
        if not client:
            client = Client(id=client_id)
            client = await self.repository.create(client)
            await self.session.commit()
        return client
