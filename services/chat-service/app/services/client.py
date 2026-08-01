import uuid
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.repositories.client import ClientRepository
from shared.database.models.client import Client

logger = logging.getLogger(__name__)

class ClientService:
    def __init__(self, session: AsyncSession, redis_client: redis.Redis = None):
        self.session = session
        self.repository = ClientRepository(session)
        self.redis = redis_client

    async def get_or_create_client(self, client_id: uuid.UUID) -> Client:
        cache_key = f"client:{client_id}"
        
        if self.redis:
            cached_client = await self.redis.get(cache_key)
            if cached_client:
                logger.info(f"Cache hit for client: {client_id}")
                data = json.loads(cached_client)
                return Client(id=uuid.UUID(data["id"]))
            
            logger.info(f"Cache miss for client: {client_id}")

        client = await self.repository.get_by_id(client_id)
        if not client:
            logger.info(f"Creating new client: {client_id}")
            client = Client(id=client_id)
            client = await self.repository.create(client)
            await self.session.commit()
        
        if self.redis:
            await self.redis.setex(
                cache_key,
                3600,
                json.dumps({"id": str(client.id)})
            )
            
        return client
