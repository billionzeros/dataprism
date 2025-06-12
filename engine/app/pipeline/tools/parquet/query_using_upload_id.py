import logging
import dspy
import re
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

MAX_ROWS_RETURNED = 500
"""
Maximum number of rows to return from a query. This is a safeguard to prevent excessive data retrieval.
"""
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

        fetch_limit = MAX_ROWS_RETURNED + 1

        if re.search(r'LIMIT\s+\d+', sql_query, re.IGNORECASE):
            final_sql = re.sub(r'LIMIT\s+\d+', f'LIMIT {fetch_limit}', sql_query, flags=re.IGNORECASE)
        else:
            # If no LIMIT exists, add one
            final_sql = f"{sql_query.rstrip(';')} LIMIT {fetch_limit}"

        logger.info(f"Executing modified SQL: {final_sql}")

        with DuckDBConn() as duckdb_conn:
            conn = duckdb_conn.conn

            if conn is None:
                raise ValueError("DuckDB connection is not established.")

            result = conn.execute(sql_query, (s3_uri,)).fetchall()

            if len(result) > MAX_ROWS_RETURNED:
                logger.info(f"Query returned more than {MAX_ROWS_RETURNED} rows. Returning only the first {MAX_ROWS_RETURNED} rows.")
                raise ValueError(
                    f"Query returned more than {MAX_ROWS_RETURNED} rows."
                )

            return QueryResult(result=result)
    except duckdb.Error as e:
        logger.error(f"DuckDB error executing query on storage_key {storage_key}: {e}", exc_info=True)
        return QueryResult(error_message=str(e))
    
    except ValueError as ve:
        logger.error(f"ValueError while executing query on storage_key {storage_key}: {ve}", exc_info=True)
        return QueryResult(error_message=str(ve))
    
    except Exception as e:
        logger.error(f"Error executing DuckDB query on storage_key {storage_key}: {e}", exc_info=True)
        return QueryResult(error_message=str(e))
    

async def dspy_query_parquet_tool_func(upload_id: str, sql_query: str):
    """
    DSPy tool function wrapper. Executes DuckDB query in a thread.
    Returns list of rows (as dicts) or a list containing a single error dictionary.
    """
    logger.info(f"Executing query using upload_id {upload_id}")

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
        
        - High-Level Purpose:
        This tool executes a DuckDB SQL query against a specified Parquet file to extract data or answer questions about its contents.

        - Critical Rules for Usage (The Guardrails):
        * **Efficiency:** "You MUST write the most efficient query possible. Do not retrieve unnecessary data. Use specific column names instead of `*`."
        * **Safety:** "You MUST ALWAYS include a `LIMIT` clause to prevent data overflow. Default to `LIMIT 10` if the user doesn't specify a count."
        * **Intent:** "Analyze the user's intent. If they ask for categories or unique values, you MUST use aggregation functions like `SELECT DISTINCT` or `GROUP BY`."
        * **Syntax:** "e.g., 'The SQL query MUST contain `read_parquet(?)` as the table name.'"

        Common Scenarios & Examples (Show, Don't Just Tell):
        - **Scenario 1:** User wants to retrieve specific columns from a Parquet file.
            - Example Query: `SELECT column1, column2 FROM read_parquet(?) WHERE column1 = 'some_value' LIMIT 10;`
        - **Scenario 2:** User wants to count the number of unique values in a column.  
            - Example Query: `SELECT COUNT(DISTINCT column1) FROM read_parquet(?);`
        - **Scenario 3:** User wants to filter data based on a condition.
            - Example Query: `SELECT column1, column2 FROM read_parquet(?) WHERE column1 > 100 LIMIT 10;`
        - **Scenario 4:** User wants to aggregate data.
            - Example Query: `SELECT column1, COUNT(*) FROM read_parquet(?) GROUP BY column1 LIMIT 10;`
        - **Scenario 5:** User wants to retrieve the first 5 rows of a Parquet file.
            - Example Query: `SELECT * FROM read_parquet(?) LIMIT 5;`
        """
    ),
    func=dspy_query_parquet_tool_func,
    arg_types={
        "upload_id": str,
        "sql_query": str,
    },
    arg_desc={
        "upload_id": "The unique identifier of the upload record. This ID is used to locate the Parquet file in R2 storage. Example: '123e4567-e",
        "sql_query": "DuckDB SQL query using 'read_parquet(?)' (e.g., 'SELECT * FROM read_parquet(?) LIMIT 5;').",
    }
)