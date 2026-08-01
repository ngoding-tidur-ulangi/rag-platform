import uuid
import logging
from typing import AsyncGenerator
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.config.database import get_db as _get_db
from app.config.settings import settings
from app.services.client import ClientService
from shared.database.models.client import Client

logger = logging.getLogger(__name__)

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        raise
    finally:
        await client.close()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in _get_db():
        yield session

async def get_current_client(
    x_client_id: str = Header(..., alias="X-Client-ID"),
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
) -> Client:
    try:
        client_uuid = uuid.UUID(x_client_id)
    except ValueError:
        logger.warning(f"Invalid X-Client-ID format received: {x_client_id}")
        raise HTTPException(status_code=400, detail="Invalid X-Client-ID format. Must be a valid UUID.")
    
    service = ClientService(db, redis_client)
    client = await service.get_or_create_client(client_uuid)
    return client
