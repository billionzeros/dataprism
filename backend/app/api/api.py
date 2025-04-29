from fastapi import APIRouter

from .routers import health

api_router = APIRouter()

# Include the API routers
api_router.include_router(health.router, prefix="/healthz", tags=["health"])