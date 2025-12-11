"""
bruno-memory: Advanced memory management for bruno-ai

A high-performance, multi-backend memory system providing persistent storage
and intelligent retrieval for AI conversations and context management.
"""

import importlib.metadata
from typing import Optional

from .factory import (
    MemoryBackendFactory, 
    factory,
    create_backend, 
    create_config, 
    list_backends, 
    register_backend,
    create_from_env,
    create_with_fallback
)
from .base import (
    BaseMemoryBackend,
    MemoryConfig,
    SQLiteConfig,
    PostgreSQLConfig,
    RedisConfig,
    ChromaDBConfig,
    QdrantConfig,
    CONFIG_CLASSES
)

# Import backends to trigger auto-registration
from . import backends

# Import managers
from .managers import (
    ConversationManager,
    ContextBuilder,
    MemoryRetriever
)

from .exceptions import (
    MemoryError,
    ConnectionError,
    ConfigurationError,
    ValidationError,
    NotFoundError,
    DuplicateError,
    PermissionError,
    StorageError,
    QueryError,
    SerializationError,
    BackendNotFoundError,
    IntegrationError,
)

# Version handling with fallback
try:
    __version__ = importlib.metadata.version('bruno-memory')
except importlib.metadata.PackageNotFoundError:
    __version__ = '0.1.0'  # Fallback version

__all__ = [
    # Core classes
    'BaseMemoryBackend',
    'MemoryBackendFactory',
    'factory',
    # Configuration classes
    'MemoryConfig',
    'SQLiteConfig',
    'PostgreSQLConfig',
    'RedisConfig',
    'ChromaDBConfig',
    'QdrantConfig',
    'CONFIG_CLASSES',
    # Factory functions
    'create_backend',
    'create_config',
    'list_backends', 
    'register_backend',
    # Manager classes
    'ConversationManager',
    'ContextBuilder',
    'MemoryRetriever',
    # Exception classes
    'MemoryError',
    'ConnectionError',
    'ConfigurationError',
    'ValidationError',
    'NotFoundError',
    'DuplicateError',
    'PermissionError',
    'StorageError',
    'QueryError',
    'SerializationError',
    'BackendNotFoundError',
    'IntegrationError',
    # Version
    '__version__'
]