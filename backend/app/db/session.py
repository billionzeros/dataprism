import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    engine = create_engine(
        str(settings.database_url), 
        pool_pre_ping=True,
        max_overflow=settings.db_max_overflow,
        pool_size=settings.db_pool_size,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
    )

    # Session is used to interact with the database
    SessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=engine
    )

    logger.info("Database engine created successfully.")
except Exception as e:
    logger.critical(f"Failed to create database engine: {e}", exc_info=True)

    raise RuntimeError(f"Datase initialization failed, {e}") from e