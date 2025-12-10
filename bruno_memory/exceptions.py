"""Custom exceptions for bruno-memory package."""

from typing import Optional


class MemoryError(Exception):
    """Base exception for memory-related errors."""
    pass


class BackendError(MemoryError):
    """Raised when backend operations fail."""
    
    def __init__(self, message: str, backend_type: Optional[str] = None, original_error: Optional[Exception] = None):
        self.backend_type = backend_type
        self.original_error = original_error
        super().__init__(message)


class ConfigurationError(MemoryError):
    """Raised when configuration is invalid."""
    pass


class ConnectionError(BackendError):
    """Raised when backend connection fails."""
    pass


class StorageError(BackendError):
    """Raised when storage operations fail."""
    pass


class RetrievalError(BackendError):
    """Raised when retrieval operations fail."""
    pass


class MigrationError(MemoryError):
    """Raised when database migrations fail."""
    pass


class EmbeddingError(MemoryError):
    """Raised when embedding operations fail."""
    pass


class CompressionError(MemoryError):
    """Raised when memory compression fails."""
    pass


class ContextBuildingError(MemoryError):
    """Raised when context building fails."""
    pass


class SessionError(MemoryError):
    """Raised when session operations fail."""
    pass


class MemoryLimitExceededError(MemoryError):
    """Raised when memory limits are exceeded."""
    
    def __init__(self, message: str, current_size: Optional[int] = None, limit: Optional[int] = None):
        self.current_size = current_size
        self.limit = limit
        super().__init__(message)


class InvalidQueryError(MemoryError):
    """Raised when memory queries are invalid."""
    pass


class BackendNotAvailableError(MemoryError):
    """Raised when requested backend is not available."""
    
    def __init__(self, backend_name: str, reason: Optional[str] = None):
        self.backend_name = backend_name
        self.reason = reason
        message = f"Backend '{backend_name}' is not available"
        if reason:
            message += f": {reason}"
        super().__init__(message)