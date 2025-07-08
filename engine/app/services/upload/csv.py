import io
import logging
import uuid
import duckdb
import pandas as pd
from typing import BinaryIO, Optional
from app.utils import APP_LOGGER_NAME
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.upload import Upload as UploadModel
from app.pipeline.llm.modules.process_csv import CSVHeaderDescriptionContext
from app.pipeline.llm.modules.learning import LearningModule

from google.genai.types import ContentEmbedding
from sqlalchemy import select
from fastapi import HTTPException, status
from app.settings.config import settings
from app.services.duck_db import DuckDBConn
# from app.pipeline.modules.llmhandler.embeddings import Embedder, EmbedContentConfig, EmbeddingSourceType, EmbeddingModel

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
    

async def process_csv(
    db: AsyncSession,
    upload: UploadModel,
) -> list[ContentEmbedding]:
    """
    Processes a CSV file, using DuckDB to retrieve the headers of the CSV file.
    Generates embeddings for each header and stores them in the database.
    """
    try:

        headers: list[str] = []
        num_sample_rows = 3
        headers_context: list[CSVHeaderDescriptionContext] = []
        upload_id = upload.id

        try:
            with DuckDBConn() as duckdb_conn:
                s3_uri = f"s3://{settings.r2_bucket_name}/{upload.storage_key}"

                # DuckDB query to describe the CSV file
                describe_query = "DESCRIBE SELECT * FROM read_parquet(?);"

                conn = duckdb_conn.conn

                if conn is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to establish DuckDB connection.",
                    )

                headers_result = conn.execute(describe_query, parameters=[s3_uri]).fetchall()

                if not headers_result:
                    logger.error(f"No headers found for upload {upload_id}.")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="No headers found for the CSV file.",
                    )

                for row in headers_result:
                    context = CSVHeaderDescriptionContext(
                        header_name=row[0],
                        sample_data=[],
                    )
                    headers_context.append(context)
                    headers.append(row[0])

                logger.info(f"Successfully extracted headers for upload {upload_id}: {headers}")

                if headers:
                    sample_query = f"SELECT {', '.join(headers)} FROM read_parquet(?) LIMIT ?;"
                    sample_result = conn.execute(sample_query, parameters=[s3_uri, num_sample_rows]).fetchall()

                    if sample_result:
                        for row in sample_result:
                            for i, sample_data in enumerate(row):
                                context = headers_context[i]
                                if context is not None:
                                    context.sample_data.append(sample_data)
                    else:
                        logger.warning(f"No sample data found for upload {upload_id}.")

        except duckdb.Error as e:
            logger.error(f"DuckDB Processing Error: {e}")

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process CSV file with DuckDB.",
            )
        
        except HTTPException:
            raise
        

        process_id = uuid.uuid4()

        module = LearningModule(session_id=process_id, tools=[])

        output = await module.aforward(
            raw_metrics=headers,
            context={
                "headers_count": len(headers),
                "headers_info": [context.model_dump_json() for context in headers_context],
            }
        )


        return []
    
    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the CSV file.",
        )
