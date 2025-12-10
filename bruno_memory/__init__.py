"""Bruno Memory - Memory storage and retrieval system for Bruno AI Platform.

This package provides multiple backend storage options for conversation history,
user context, and semantic memory while maintaining a consistent API for
AI assistants to interact with.
"""

try:
    from bruno_memory.__version__ import __version__
except ImportError:
    __version__ = "0.1.0-dev"

# Import main factory for easy access
from bruno_memory.factory import MemoryFactory

# Import main exceptions for error handling
from bruno_memory.exceptions import (
    MemoryError,
    BackendError,
    ConfigurationError,
    ConnectionError,
    StorageError,
    RetrievalError,
    MigrationError,
    EmbeddingError,
    CompressionError,
    ContextBuildingError,
    SessionError,
    MemoryLimitExceededError,
    InvalidQueryError,
    BackendNotAvailableError,
)

__all__ = [
    # Version info
    "__version__",
    
    # Factory
    "MemoryFactory",
    
    # Exceptions
    "MemoryError",
    "BackendError", 
    "ConfigurationError",
    "ConnectionError",
    "StorageError",
    "RetrievalError",
    "MigrationError",
    "EmbeddingError",
    "CompressionError",
    "ContextBuildingError",
    "SessionError",
    "MemoryLimitExceededError",
    "InvalidQueryError",
    "BackendNotAvailableError",
]