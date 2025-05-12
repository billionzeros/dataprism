import io
import logging
import uuid
import pandas as pd
from typing import BinaryIO, Optional
from app.utils import APP_LOGGER_NAME
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.upload import Upload as UploadModel
from sqlalchemy import select

logger = logging.getLogger(APP_LOGGER_NAME)

async def create_upload(
    db: AsyncSession,
    upload_info: UploadModel,
) -> UploadModel:
    """
    Uploads a file to the database.
    """
    db.add(upload_info)
    await db.commit()
    await db.refresh(upload_info)

    return upload_info

async def get_uploads(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
) -> list[UploadModel]:
    """
    Retrieves all uploads from the database with pagination.
    """
    statement = select(UploadModel).offset(skip).limit(limit)
    result = await db.execute(statement)
    
    return list(result.scalars().all())

async def get_upload_by_id(
    db: AsyncSession,
    upload_id: uuid.UUID,
) -> Optional[UploadModel]:
    """
    Retrieves a file from the database by its ID.
    """
    statement = select(UploadModel).where(UploadModel.id == upload_id)
    result = await db.execute(statement)
    
    return result.scalars().first()


async def convert_csv_to_parquet_stream(
        csv_stream: BinaryIO
) -> io.BytesIO:
    """
    Reads a CSV file from a stream and converts it to a Parquet file stream.
    """

    try:
        df = pd.read_csv(csv_stream, encoding='utf-8')
        parquet_buffer = io.BytesIO()

        df.to_parquet(parquet_buffer, index=False, engine='pyarrow')
        parquet_buffer.seek(0)
        return parquet_buffer
    except pd.errors.EmptyDataError:
        logger.warning("Attempted to process an empty CSV Stream.")
        raise ValueError("CSV Stream is empty.")
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV Stream: {e}")
        raise ValueError("Error parsing CSV Stream.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise ValueError("An unexpected error occurred during CSV processing.")