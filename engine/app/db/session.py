import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from engine.app.settings.config import settings

logger = logging.getLogger(__name__)

try:
    async_db_url = str(settings.database_url).replace("postgresql://", "postgresql+asyncpg://", 1)

    connect_args = {}

    connect_args["ssl"] = "require"

    async_engine = create_async_engine(
        async_db_url,
        pool_pre_ping=True,
        max_overflow=settings.db_max_overflow,
        pool_size=settings.db_pool_size,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        connect_args=connect_args,
    )

    # Session is used to interact with the database
    AsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        autocommit=False, 
        autoflush=False, 
        expire_on_commit=False,
    )

    logger.info("Database engine created successfully.")
except Exception as e:
    logger.critical(f"Failed to create database engine for URL '{settings.database_url}': {e}", exc_info=True)

    raise RuntimeError(f"Datase initialization failed, {e}") from e