import logging
import uuid
import threading
from typing import List, Dict
from app.utils.logging_config import APP_LOGGER_NAME
from .postgres import PostgresRunner, PostgressRunnerConfig, PostgresRunnerError, PostgresEndpoint
from ._utils import BaseMcpRunner

logger = logging.getLogger(APP_LOGGER_NAME)

class MCPManager:
    """
    Manager different MCP [ Model Context Protocols ] ( postgres, redis, etc. ) and theier connections.
    """
    def __init__(self, host_port_range_start=8001, host_port_range_end=9000):
        self._available_host_ports: List[int] = list(range(host_port_range_start, host_port_range_end + 1))
        """
        Available host ports for MCP services, starting from `host_port_range_start` to `host_port_range_end`.
        """

        self._project_to_port: Dict[str, int]  = {}
        """
        Mapping of project names to their allocated host ports.
        """

        self._port_to_project: Dict[int, str] = {}
        """
        Mapping of host ports to their corresponding project names.
        """

        self._port_lock = threading.Lock()
        """
        Thread-safe lock to manage access to the available host ports.
        """

        self._running_mcps: Dict[str, BaseMcpRunner] = {}
        """
        Dictionary to keep track of running MCP instances, keyed by project name.
        """

    def _allocate_host_port(self, project_name) -> int | None:
        with self._port_lock:
            if not self._available_host_ports:
                logging.warning("No available host ports left.")
                return None
            
            port = self._available_host_ports.pop(0)
            self._port_to_project[port] = project_name

            logging.info(f"Allocated host port {port} for project {project_name}")
            return port
        
    def _release_host_port(self, project_name) -> None:
        with self._port_lock:
            if project_name not in self._project_to_port:
                logging.warning(f"Project {project_name} does not have an allocated port.")
                return
            
            port = self._project_to_port.pop(project_name)
            self._port_to_project.pop(port, None)
            self._available_host_ports.append(port)

            logging.info(f"Released host port {port} for project {project_name}")

    def start_pg_mcp(self, db_endpoint: PostgresEndpoint, project_name: str) -> PostgresRunner | None:
        """
        Returns a Postgres MCP instance for the given project name.
        Allocates a host port for the project if not already allocated.
        """
        try:
            port = self._allocate_host_port(project_name)
            if port is None:
                return None
            
            logging.info(f"Creating PostgresRunner for project {project_name} on port {port}")

            runner_uid = uuid.uuid4().hex

            runner_config = PostgressRunnerConfig(
                runner_uid=runner_uid,
                runner_name=project_name,
                database_endpoint=db_endpoint,
                host_port=port,
            )

            postgres_runner = PostgresRunner(config=runner_config)

            postgres_runner.start()

            logging.info(f"PostgresRunner started for project {project_name} on port {port}")

            self._running_mcps[project_name] = postgres_runner

        except PostgresRunnerError as e:
            logging.error(f"Failed to start PostgresRunner for project {project_name}: {e}")
            self._release_host_port(project_name)

            raise Exception(f"Failed to start PostgresRunner for project {project_name}: {e}")
            
        except Exception as e:
            logging.error(f"Error allocating port for project {project_name}: {e}")

            self._release_host_port(project_name)
            raise e