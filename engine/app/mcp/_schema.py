class BaseMcpRunner:
    """
    Base class for MCP (Model Context Protocol) runners.
    This class provides common functionality for managing MCP services.
    """
    def start(self):
        raise NotImplementedError("Subclasses must implement the start method.")
    
    @property
    def runner_uid(self):
        raise NotImplementedError("Subclasses must implement the runner_uid property.")
    
    @property
    def runner_addr(self):
        raise NotImplementedError("Subclasses must implement the runner_addr property.")