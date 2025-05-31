class BaseMcpRunner:
    """
    Base class for MCP (Model Context Protocol) runners.
    This class provides common functionality for managing MCP services.
    """
    def start(self):
        """Starts the MCP service."""
        raise NotImplementedError("Subclasses must implement the start method.")
    
    def stop(self):
        """Stops the MCP service."""
        raise NotImplementedError("Subclasses must implement the stop method.")

    def health_check(self) -> bool:
        """
        Checks the health of the MCP service.
        Returns:
            bool: True if healthy, False otherwise.
        """
        raise NotImplementedError("Subclasses must implement the health_check method.")
    
    @property
    def runner_uid(self) -> str:
        """Unique identifier for the runner instance."""
        raise NotImplementedError("Subclasses must implement the runner_uid property.")
    
    @property
    def runner_addr(self) -> str:
        """
        Address or name used for managing the runner instance (e.g., Docker Compose project name).
        """
        raise NotImplementedError("Subclasses must implement the runner_addr property.")