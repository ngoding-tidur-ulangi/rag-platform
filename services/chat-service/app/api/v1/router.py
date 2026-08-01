from fastapi import APIRouter
from app.api.v1.controllers import health, conversation, message

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(conversation.router, tags=["conversation"])
api_router.include_router(message.router, tags=["message"])
