import logging
import dspy
import uuid
from typing import Any, Optional
from pydantic import BaseModel
from app.settings.config import settings
from app.services.duck_db import DuckDBConn
from app.utils import APP_LOGGER_NAME
from app.db.session import AsyncSessionLocal 
from app.db.models.upload import Upload as UploadModel 

logger = logging.getLogger(APP_LOGGER_NAME)

class FileSchemaResult(BaseModel):
    upload_id: str
    """
    Unique identifier for the uploaded file, typically a UUID string.
    """

    storage_key: Optional[str] = None
    """
    Storage key in the database or object storage where the file is stored, Right now stored on R2 Bucket.
    """

    file_name: Optional[str] = None
    """
    Name of the file associated with the upload_id, if available.
    """

    header_result: Optional[Any] = None
    """
    The result of the header description query, which includes schema information.
    """

    error_message: Optional[str] = None
    """
    Error message if any error occurs while fetching the schema.
    """


async def _fetch_upload_record(upload_id: str) -> UploadModel:
    """
    Fetches the upload record from the database using the provided upload_id.
    Returns None if the record is not found or if an error occurs.
    """
    try:
        upload_uuid = uuid.UUID(upload_id)
    except ValueError:
        logger.error(f"Invalid UUID format for upload_id: {upload_id}")
        raise ValueError(f"Invalid UUID format for upload_id: {upload_id}") 
    
    except Exception as e:
        logger.error(f"Unexpected error while parsing upload_id {upload_id}: {e}", exc_info=True)
        raise ValueError(f"Unexpected error while parsing upload_id {upload_id}: {str(e)}")

    async with AsyncSessionLocal() as db:
        try:
            upload_record = await db.get(UploadModel, upload_uuid)
            if not upload_record:
                logger.warning(f"Upload record not found for upload_id: {upload_uuid}")
                raise ValueError(f"Upload record not found for upload_id: {upload_uuid}")
            
            return upload_record
        
        except ValueError as ve:
            logger.error(f"ValueError while fetching upload record for upload_id {upload_uuid}: {ve}")
            raise ve

        except Exception as e:
            logger.error(f"Database error while fetching upload record for upload_id {upload_uuid}: {e}", exc_info=True)
            raise e

async def _fetch_schema_from_db(upload_id: str):
    logger.info(f"Fetching schema from DB for upload_id: {upload_id}")

    try:
        upload_record = await _fetch_upload_record(upload_id)

        try:
            logger.info(f"Upload record found for upload_id {upload_id}: {upload_record.storage_key}")

            s3_uri = f"s3://{settings.r2_bucket_name}/{upload_record.storage_key}"

            describe_query = "DESCRIBE SELECT * FROM read_parquet(?);"

            with DuckDBConn() as duck_conn:
                conn = duck_conn.conn
                
                if conn is None:
                    raise ValueError("DuckDB connection is not established.")
                
                header_result = conn.execute(describe_query, (s3_uri,)).fetchall()

                if not header_result:
                    raise ValueError(f"No schema information found for upload_id: {upload_id}. The file might not be a valid Parquet file or is empty.")
                
                return FileSchemaResult(
                    upload_id=upload_id,
                    file_name=upload_record.file_name,
                    header_result=header_result,
                    error_message=None
                )
        except ValueError as ve:
            logger.error(f"ValueError while querying upload_id: {upload_id} storage_key: {upload_record.storage_key}: {ve}")
            raise ve
        
        except Exception as e:
            logger.error(f"Error while querying upload_id: {upload_id} storage_key: {upload_record.storage_key}: {e}", exc_info=True)
            raise e

    except ValueError as ve:
        logger.error(f"ValueError while fetching upload record for upload_id {upload_id}: {ve}")
        return FileSchemaResult(upload_id=upload_id, error_message=str(ve))

    except Exception as e:
        logger.error(f"Error fetching upload record for upload_id {upload_id}: {e}", exc_info=True)
        return FileSchemaResult(upload_id=upload_id, error_message=f"An error occurred while fetching the upload record: {str(e)}")

async def get_parquet_schema_func(upload_id: str):
    """
    DSPy tool function to retrieve schema information for a given upload_id.
    Returns a list of column schema details, or a list containing a single error dictionary.
    """
    logger.info(f"Getting Parquet file schema for upload_id: {upload_id}")

    result = await _fetch_schema_from_db(upload_id)

    if not isinstance(result, FileSchemaResult):
        return FileSchemaResult(
            upload_id=upload_id,
            error_message="Unexpected result type from schema fetch function. Expected FileSchemaResult."
        )

    return result

GetParquetFileSchemaTool = dspy.Tool(
    name="GetParquetFileSchema",
    desc=(
        "Retrieves the schema for uploaded and processed file (e.g., Parquet, CSV) using its Upload ID. "
        "This information is essential for constructing accurate SQL queries"
        "Use this tool *before* attempting to query a file if its schema is not precisely known. "
        "Returns a list of dictionaries, where each dictionary describes a column. "
        "If an error occurs or no schema is found, it returns a list containing a single dictionary with an 'error' or 'warning' key."
    ),
    func=get_parquet_schema_func,
    arg_types={
        "upload_id": str,
    },
    arg_desc={
        "upload_id": "Unique ID (UUID string) of the file whose schema is needed.",
    }
)