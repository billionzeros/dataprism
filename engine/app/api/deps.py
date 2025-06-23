import logging
from typing import AsyncGenerator
from app.cloud.cf.r2_client import R2Client
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.mcp import MCPManager

from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    Ensures the session is automatically closed afterwards.
    """
    db: AsyncSession | None = None
    try:
        db = AsyncSessionLocal()
        yield db

        await db.commit()

    except HTTPException as http_exc:
        if db is not None:
            await db.rollback()
        
        raise http_exc
    
    except Exception as e:
        logger.error(f"Error creating database session: {e}", exc_info=True)
        if db is not None:
            await db.rollback()
        
        raise
    finally:
        if db is not None:
            try:
                await db.close()   
            except Exception as e:
                logger.error(f"Error closing database session: {e}", exc_info=True)


def get_r2_client(request: Request):
    """
    FastAPI dependency that provides a R2 client per request.
    """
    r2_client: R2Client | None = getattr(request.app.state, "r2_client", None)

    if r2_client is None or not r2_client:
        logger.error("R2 client dependency requested, but client is not available or not initialized.")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Storage client is not available or not initialized."
        )
    
    return r2_client

def get_mcp_manager(request: Request):
    """
    FastAPI dependency that provides a MCP manager per request.
    """
    mcp_manager: MCPManager | None = getattr(request.app.state, "mcp_manager", None)

    if mcp_manager is None or not mcp_manager:
        logger.error("MCP manager dependency requested, but manager is not available or not initialized.")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MCP manager is not available or not initialized."
        )
    
    return mcp_manager