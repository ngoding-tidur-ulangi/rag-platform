from fastapi import APIRouter
from app.api.v1.controllers import retrieval, health

api_router = APIRouter()
api_router.include_router(retrieval.router, tags=["retrieval"])
api_router.include_router(health.router, tags=["health"])
