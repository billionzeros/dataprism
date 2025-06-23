import os
import logging
from pathlib import Path
import shutil
import subprocess

from typing import List, Dict
from ._schema import PostgressRunnerConfig, PostgresRunnerError
from .._utils import BaseMcpRunner
from app.utils.logging_config import APP_LOGGER_NAME

logger = logging.getLogger(APP_LOGGER_NAME)

class PostgresRunner(BaseMcpRunner):
    def __init__(self, config: PostgressRunnerConfig):
        self._image_name = "crystaldba/postgres-mcp:latest"
        """
        The Docker image name for the Postgres MCP service
        """

        self._compose_template_file = str(Path(__file__).parent / "docker-compose.yaml")
        """
        Path to the Docker Compose File for the Postgres Service.
        """
        if not Path(self._compose_template_file).exists():
            logger.warning(f"Compose template file not found at {self._compose_template_file}. This might cause errors.")

        self._docker_compose_cmd = self._find_docker_compose()
        """
        The Docker Compose command to be used, either `docker-compose` or `docker compose`.
        """

        self._config: PostgressRunnerConfig = config
        """
        Configuration for the PostgresRunner, including database URI, host port, and access mode.
        """

    @property
    def runner_uid(self):
        """
        Returns the unique identifier for the Postgres runner.
        """
        return self._config.runner_uid
    
    @property
    def _runner_name(self):
        """
        Returns the name of the Postgres runner, which is used to identify the service instance.

        Defaults to "postgres_runner" if not specified in the configuration.
        """
        return self._config.runner_name

    @property
    def runner_addr(self):
        """
        Runner address is a combination of the runner name and its unique identifier.
        If the unique identifier is not set, it returns just the runner name.
        """
        # Sanitize for Docker project name (alphanumeric and hyphens/underscores)
        sanitized_name = "".join(c if c.isalnum() else "_" for c in self._runner_name)
        sanitized_uid = "".join(c if c.isalnum() else "_" for c in self.runner_uid)

        return f"{sanitized_name}_{sanitized_uid}"
    
    @property
    def runner_sse_endpoint(self):
        """
        Returns the SSE endpoint for the Postgres service.
        This is typically used for streaming updates or notifications from the Postgres service.
        """
        return f"http:/127.0.0.1:{self.host_port}/sse"

    @property
    def _database_uri(self):
        """
        Returns the database URI for the Postgres service.
        """
        return self._config.database_endpoint.to_postgresql_uri()
    
    @property
    def host_port(self):
        """
        Returns the host port on which the Postgres service will be exposed.
        eg. 8001
        """
        return self._config.host_port
    
    @property
    def mcp_container_port(self):
        """
        Returns the container port for the Postgres MCP service.
        This is typically set to 5432, which is the default port for Postgres.
        """
        return self._config.mcp_container_port
    
    @property
    def access_mode(self):
        """
        Returns the access mode for the Postgres service.
        """
        return self._config.access_mode
    
    def start(self,):
        """
        Starts the Postgres MCP service using Docker Compose.
        This method will create a Docker Compose project with the specified configuration
        and start the Postgres service in a Docker container.
        Raises:
            PostgresRunnerError: If the Docker Compose command fails or if the Docker Compose executable is not found.
        """
        logger.info(f"Starting Postgres MCP service for project {self.runner_addr} on port {self.host_port}")

        env_vars = {
            "MCP_IMAGE_NAME": self._image_name,
            "MCP_CONTAINER_NAME": "mcp",
            "DATABASE_URI": self._database_uri,
            "MCP_HOST_PORT": str(self.host_port),
            "MCP_CONTAINER_PORT": str(self.mcp_container_port),
            "MCP_ACCESS_MODE": self.access_mode,
            "RUNNER_UID_LABEL": "mcp"
        }

        self._run_compose_command(["up", "-d", "--remove-orphans", "--force-recreate"], env_vars)
        logger.info(f"Postgres MCP service {self.runner_addr} initiated successfully.")

    def stop(self):
        logger.info(f"Stopping Postgres MCP service {self.runner_addr}")
        try:
            self._run_compose_command(["down", "--remove-orphans", "--volumes"], check_call=False)
            logger.info(f"Postgres MCP service {self.runner_addr} stopped.")

        except PostgresRunnerError as e:
            logger.error(f"Error stopping Postgres MCP service {self.runner_addr}: {e}. Manual cleanup might be required.")

    def _find_docker_compose(self, ):
        """
        Find the Docker Compose executable in the system PATH.
        """
        if cmd := shutil.which("docker-compose"): # Python 3.8+
            return [cmd]
        
        if cmd := shutil.which("docker"):
            try:
                result = subprocess.run([cmd, "compose", "--version"], capture_output=True, text=True, check=False)
                if result.returncode == 0 and "Docker Compose version" in result.stdout:
                    return [cmd, "compose"]
            except FileNotFoundError:
                logger.error("Docker Compose command not found in the system PATH.")
                raise PostgresRunnerError("Docker Compose executable not found. Please install Docker Compose or ensure it is in your PATH.")

        raise PostgresRunnerError("Docker Compose executable not found. Please ensure Docker Compose is installed and in your PATH.")

    def _run_compose_command(self, command: List[str], env_vars: Dict[str, str] | None = None, check_call: bool = True) -> subprocess.CompletedProcess:
        """
        Run a Docker Compose command with the specific project name and env variables.
        """
        if not Path(self._compose_template_file).is_file():
            raise PostgresRunnerError(f"Docker Compose template file not found: {self._compose_template_file}")
        
        cmd_prefix = self._docker_compose_cmd + ["-f", self._compose_template_file, "-p", self.runner_addr]

        full_cmd = cmd_prefix + command

        process_env = os.environ.copy()

        if env_vars is not None:
            process_env.update(env_vars)

        try:
            result = subprocess.run(full_cmd, env=process_env, capture_output=True, text=True, check=True)
            logger.info(f"Docker Compose command executed successfully for project {self.runner_addr}: {result.stdout.strip()}")
            if result.stderr:
                    logger.warning(f"Compose command stderr for {self.runner_addr}:\n{result.stderr}")

            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker Compose command failed for project {self.runner_addr}: {e}")
            raise PostgresRunnerError(f"Failed to run Docker Compose command for project {self.runner_addr}: {e}")

        except FileNotFoundError as e:
            logger.error(f"Docker Compose executable not found: {e}")
            raise PostgresRunnerError("Docker Compose executable not found. Please ensure Docker Compose is installed and in your PATH.")

        except Exception as e:
            logger.error(f"An unexpected error occurred while running Docker Compose command: {e}")
            raise
        
