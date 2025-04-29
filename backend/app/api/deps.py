from typing import Generator
from sqlalchemy.orm import Session
import logging

# Import SessionLocal which is configured in app.db.session
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy database session per request.
    Ensures the session is automatically closed afterwards.
    """
    db: Session | None = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        logger.error(f"Error creating database session: {e}", exc_info=True)
        raise
    finally:
        if db is not None:
            try:
                db.close()   
            except Exception as e:
                logger.error(f"Error closing database session: {e}", exc_info=True)
