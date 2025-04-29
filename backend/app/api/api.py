from fastapi import APIRouter

from .routers import health, workspace

api_router = APIRouter()

# Include the API routers
api_router.include_router(health.router, prefix="/healthz", tags=["health"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])