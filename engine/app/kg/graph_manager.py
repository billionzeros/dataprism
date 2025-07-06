import logging
from threading import Lock
from neo4j import GraphDatabase, exceptions
from app.settings.config import settings
from app.utils.logging_config import APP_LOGGER_NAME
from ._error import GraphError

# Configure a logger for better debugging and monitoring in production
logger = logging.getLogger(APP_LOGGER_NAME).getChild("kg.graph_manager")

class KnowledgeGraph:
    """
    A thread-safe Singleton class to manage the connection to a Neo4j database.

    This class ensures only one connection driver is instantiated across the application,
    handles connection verification, and provides a clean interface for executing queries
    and closing the connection.
    """
    _instance = None
    _lock = Lock()  # To ensure thread-safety during instantiation

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initializes the Neo4j driver connection.
        This is designed to be idempotent; it will only run the connection logic once.
        """
        if hasattr(self, 'driver'):
            logger.warning("KnowledgeGraph instance already initialized. Skipping re-initialization.")
            return

        self.driver = None
        try:
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=settings.neo4j_max_connection_lifetime,
                max_connection_pool_size=settings.neo4j_max_connection_pool_size,
                encrypted=settings.neo4j_encrypted
            )
            self.driver.verify_connectivity()
            logger.info("Successfully connected to Neo4j.")
            self._ensure_constraints()
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Neo4j connection failed: {e}")
            self.driver = None
            raise GraphError(f"Failed to connect to Neo4j SERVICE_UNAVAILABLE: {e}")
        
        except Exception as e:
            logger.error(f"🔥 An unexpected error occurred during Neo4j setup: {e}")
            if self.driver:
                self.driver.close()
            self.driver = None
            raise

    def _ensure_constraints(self):
        """Ensures the database has the necessary constraints for data integrity."""
        if not self.driver:
            logger.error("Cannot ensure constraints, no valid driver available.")
            return
        
        try:
            with self.driver.session(database="neo4j") as session:
                session.run(
                    """
                    CREATE CONSTRAINT unique_node_source IF NOT EXISTS
                    FOR (n:Node) REQUIRE (n.raw_name, n.source_file) IS UNIQUE
                    """
                )
            logger.info("Graph constraints ensured.")
        except exceptions.ClientError as e:
            logger.error(f"Failed to ensure constraints: {e}")
            raise GraphError(f"Failed to ensure constraints in Neo4j: {e}")

    def close(self):
        """Closes the Neo4j connection driver if it exists."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed.")
            KnowledgeGraph._instance = None

    def query(self, cypher_query, params=None):
        """
        A general method to run Cypher queries.

        Args:
            cypher_query (str): The Cypher query to be executed.
            params (dict, optional): A dictionary of parameters to pass to the query.

        Returns:
            list: A list of dictionaries representing the query result records.
        
        Raises:
            Exception: If the driver is not initialized or the query fails.
        """
        if not self.driver:
            raise Exception("Driver not initialized. Cannot run query.")
        
        try:
            with self.driver.session(database="neo4j") as session:
                result = session.run(cypher_query, params or {})
                return [record.data() for record in result]
        except exceptions.ServiceUnavailable as e:
            logger.error(f"Connection to Neo4j lost. Please reconnect. Error: {e}")
            raise GraphError(f"Connection to Neo4j lost: {e}")
        
        except exceptions.ClientError as e:
            logger.error(f"Cypher query failed: {e.code} - {e.message}")
            logger.error(f"Query: {cypher_query} | Params: {params}")
            raise

        except Exception as e:
            logger.error(f"An unexpected error occurred while executing the query: {e}")
            raise GraphError(f"An unexpected error occurred while executing the query: {e}")