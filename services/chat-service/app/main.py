from fastapi import FastAPI
from app.api.v1.router import api_router
from app.config.settings import settings
from app.api.exception_handler import init_exception_handlers

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

init_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Chat Service API"}
