import logging
import dspy
import duckdb
import asyncio
import uuid
from pydantic import BaseModel
from typing import Optional, Any
from app.db.models.upload import Upload as UploadModel 
from app.services.duck_db import DuckDBConn
from app.db.session import AsyncSessionLocal
from app.utils import APP_LOGGER_NAME
from app.core.config import settings

logger = logging.getLogger(APP_LOGGER_NAME)

class QueryResult(BaseModel):
    """
    Represents the Result of a query executed on a Parquet file.
    """
    result: Optional[Any] = None
    """
    The result of the query execution, which can be any type depending on the query.
    """

    error_message: Optional[str] = None
    """
    Error message if any error occurs during query execution.
    """

async def _fetch_upload_record(upload_id: str) -> Optional[UploadModel]:
    """
    Fetches the upload record from the database using the provided upload_id.
    Returns None if the record is not found or if an error occurs.
    """
    try:
        upload_uuid = uuid.UUID(upload_id)
    except ValueError:
        logger.error(f"Invalid UUID format for upload_id: {upload_id}")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error while parsing upload_id {upload_id}: {e}", exc_info=True)
        return None

    async with AsyncSessionLocal() as db:
        try:
            upload_record = await db.get(UploadModel, upload_uuid)
            if not upload_record:
                logger.warning(f"Upload record not found for upload_id: {upload_uuid}")
                return None
            
            return upload_record
        except Exception as e:
            logger.error(f"Database error while fetching upload record for upload_id {upload_uuid}: {e}", exc_info=True)
            return None
        

def _execute_duckdb_query(storage_key: str, sql_query: str) -> QueryResult:
    try:
        s3_uri = f"s3://{settings.r2_bucket_name}/{storage_key}"

        with DuckDBConn() as duckdb_conn:
            conn = duckdb_conn.conn

            if conn is None:
                raise ValueError("DuckDB connection is not established.")

            result = conn.execute(sql_query, (s3_uri,)).fetchall()

            logger.info("Query Executed, Result", result)

            return QueryResult(result=result)
    except duckdb.Error as e:
        logger.error(f"DuckDB error executing query on storage_key {storage_key}: {e}", exc_info=True)
        return QueryResult(error_message=str(e))
    
    except Exception as e:
        logger.error(f"Error executing DuckDB query on storage_key {storage_key}: {e}", exc_info=True)
        return QueryResult(error_message=str(e))
    

async def dspy_query_parquet_tool_func(upload_id: str, sql_query: str, max_rows_to_return: int = 10):
    """
    DSPy tool function wrapper. Executes DuckDB query in a thread.
    Returns list of rows (as dicts) or a list containing a single error dictionary.
    """
    logger.info(f"Executing query using upload_id {upload_id} with SQL: {sql_query}")

    upload_record = await _fetch_upload_record(upload_id)
    if not upload_record:
        return QueryResult(
            error_message=f"Upload record not found for upload_id: {upload_id}"
        )
    if not upload_record.storage_key:
        return QueryResult(
            error_message=f"No storage key found for upload_id: {upload_id}"
        )
    
    storage_key = upload_record.storage_key

    output = await asyncio.to_thread(
        _execute_duckdb_query,
        storage_key,
        sql_query,
    )

    if output.error_message:
        return QueryResult(
            error_message=output.error_message
        )
    
    if output.result is None:
        return QueryResult(
            error_message="No results returned from the query."
        )

    return output.result



QueryParquetFileUsingUploadIdTool = dspy.Tool(
    name="QueryParquetFileUsingUploadIdTool",
    desc=(
        """
        Executes an SQL query on a specified Parquet file stored in R2 cloud storage using DuckDB.
        The SQL query MUST include 'read_parquet(?)' where the '?' will be replaced by the file's S3 URI.
        Example SQL: 'SELECT column1, column2 FROM read_parquet(?) WHERE column1 = ''some_value''.
        Returns a list of dictionaries, where each dictionary represents a row (keys are column names).
        If an error occurs, it returns a list containing a single dictionary with an 'error' key and the 'query_attempted'.


        Important: 
        - The SQL query must use 'read_parquet(?)' to reference the Parquet file.
        - Make sure you always create the most specific query possible to avoid performance issues and not make queries super expensive.
        - The LLM should ensure the query is valid DuckDB SQL.
        - The maximum number of rows to return can be controlled by the 'max_rows_to_return' parameter.
        """
    ),
    func=dspy_query_parquet_tool_func,
    args={
        "upload_id": dspy.InputField(
            name="upload_id",
            desc="The unique identifier of the upload record. This ID is used to locate the Parquet file in R2 storage. Example: '123e4567-e89b-12d3-a456-426614174000'.",
            type=str,
        ),
        "sql_query": dspy.InputField(
            name="sql_query",
            desc="The DuckDB SQL query to execute. IMPORTANT: The query MUST use 'read_parquet(?)' to reference the Parquet file. The tool will substitute '?' with the actual S3 URI of the file. Example: 'SELECT COUNT(*) FROM read_parquet(?);' or 'SELECT specific_column FROM read_parquet(?) WHERE other_column > 100 LIMIT 10;'. The LLM should ensure the query is valid DuckDB SQL.",
            type=str,
        ),
        "max_rows_to_return": dspy.InputField(
            name="max_rows_to_return",
            desc="The maximum number of data rows to return from the query. Defaults to 10. For optimal performance, the LLM should try to include a LIMIT clause in the 'sql_query' itself if a specific number of rows is desired.",
            type=int,
            default=10,
            min_value=1
        ),
    },
    arg_types={
        "upload_id": str,
        "sql_query": str,
        "max_rows_to_return": int,
    },
    arg_desc={
        "upload_id": "The unique identifier of the upload record. This ID is used to locate the Parquet file in R2 storage. Example: '123e4567-e",
        "sql_query": "DuckDB SQL query using 'read_parquet(?)' (e.g., 'SELECT * FROM read_parquet(?) LIMIT 5;').",
        "max_rows_to_return": "Maximum rows to fetch (default: 10). Results may be truncated if query yields more."
    }
)