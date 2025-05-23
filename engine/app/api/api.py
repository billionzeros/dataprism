from fastapi import APIRouter

from .routers import health, workspace, upload, chat

api_router = APIRouter()

# Include the API routers
api_router.include_router(health.router, prefix="/healthz", tags=["health"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])