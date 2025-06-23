# Custom exceptions for PostgresRunner operations
from typing import Literal
from pydantic import BaseModel, Field

class PostgresRunnerError(Exception):
    """
    Custom exception for errors related to PostgresRunner operations.
    """
    pass

class PostgresEndpoint(BaseModel):
    """
    Represents a Valid Postgres endpoint.
    """
    host: str = Field(..., description="The host address of the Postgres service.")
    """
    The host address of the Postgres service.
    """

    port: int = Field(..., description="The port number on which the Postgres service is running.")
    """
    The port number on which the Postgres service is running.
    """

    database: str = Field(..., description="The name of the database to connect to.")
    """
    The name of the database to connect to.
    """

    user: str = Field(..., description="The username for authenticating with the Postgres service.")
    """
    The username for authenticating with the Postgres service.
    """

    password: str = Field(..., description="The password for authenticating with the Postgres service.")
    """
    The password for authenticating with the Postgres service.
    """

    def to_postgresql_uri(self) -> str:
        """
        Converts the PostgresEndpoint to a database URI string.
        
        Returns:
            str: The database URI in the format `postgresql://user:password@host:port/database`.
        """
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"

    def __repr__(self) -> str:
        return f"PostgresEndpoint(host={self.host}, port={self.port}, database={self.database}, user={self.user})"

class PostgressRunnerConfig(BaseModel):
    """
    Configuration for the PostgresRunner.
    """

    runner_uid: str = Field(..., description="The unique identifier for the Postgres runner.")
    """
    The unique identifier for the Postgres runner, used to manage the service instance.
    """

    runner_name: str = Field(default="postgres_runner", description="The name of the Postgres runner.")
    """
    The name of the Postgres runner, used to identify the service instance.
    """

    database_endpoint: PostgresEndpoint = Field(..., description="The endpoint for the Postgres database.")
    """
    The endpoint for the Postgres database, including host, port, database name, user, and password.
    """

    host_port: int = Field(..., description="The host port on which the Postgres service will be exposed.")
    """
    The host port on which the Postgres service will be exposed.
    """

    mcp_container_port: int = Field(default=8000, description="The container port for the Postgres MCP service.")
    """
    The container port for the Postgres MCP service, typically set to 8000, which is the default port for Postgres.
    """
    
    access_mode: Literal["restricted", "unrestricted"] = Field(default="restricted", description="Access mode for the Postgres service.")
    """
    Access mode for the Postgres service, either 'restricted' or 'unrestricted'.
    """

    class Config:
        model_config = {"arbitrary_types_allowed": True}