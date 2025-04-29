from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# Import SessionLocal which is configured in app.db.session
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    Ensures the session is automatically closed afterwards.
    """
    db: AsyncSession | None = None
    try:
        db = SessionLocal()
        yield db

        await db.commit()
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
