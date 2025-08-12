from fastapi import APIRouter

from .routers import health, workspace, upload, chat, mcp, matrix, code

api_router = APIRouter()

# Include the API routers
api_router.include_router(health.router, prefix="/healthz", tags=["health"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(code.router, prefix="/code", tags=["code"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(matrix.router, prefix="/matrix", tags=["matrix"])
