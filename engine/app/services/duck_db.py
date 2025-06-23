import logging
import duckdb
from app.utils import APP_LOGGER_NAME
from app.settings.config import settings

logger = logging.getLogger(APP_LOGGER_NAME)

class DuckDBConn:
    """
    DuckDBConn is manages and creates DuckDB connections.
    """
    def __init__(self,):
        self._connection: duckdb.DuckDBPyConnection | None = None

    @property
    def conn(self):
        return self._connection

    def __enter__(self):
        """
        Enters the context manager and initializes the DuckDB connection.
        """
        logger.info("Initializing DuckDB connection")

        self._connection = duckdb.connect(database=':memory:', read_only=False)

        try:
            self._connection.execute("PRAGMA threads=4") # Set the number of threads to 4
            self._connection.execute("INSTALL httpfs;")
            self._connection.execute("LOAD httpfs;")
            self._connection.execute(f"SET s3_endpoint='{settings.r2_account_id}.r2.cloudflarestorage.com/{settings.r2_bucket_name}';")
            self._connection.execute(f"SET s3_access_key_id='{settings.r2_access_key_id}';")
            self._connection.execute(f"SET s3_secret_access_key='{settings.r2_secret_access_key}';")
            self._connection.execute("SET s3_use_ssl=true;")
            self._connection.execute("SET s3_region='auto';")
            self._connection.execute("SET s3_url_style='path';")
        except duckdb.Error as e:
            logger.error(f"Failed to configure DuckDB connection: {e}")
            if self._connection:
                self._connection.close()
            
            self._connection = None
            raise

        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context manager and closes the DuckDB connection.
        """
        if self._connection:
            self._connection.close()
            logger.info("DuckDB connection closed.")

        self._connection = None
