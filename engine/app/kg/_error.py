class GraphError(Exception):
    """Base class for all graph-related errors."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message