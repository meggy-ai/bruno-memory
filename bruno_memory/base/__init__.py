"""
Base implementations for bruno-memory.

This module contains abstract base classes and common utilities
that all memory backends can use.

Classes:
    BaseMemoryBackend: Abstract base class for memory backends
    Configuration Models: Backend-specific configuration classes
"""

from bruno_memory.base.base_backend import BaseMemoryBackend
from bruno_memory.base.memory_config import (
    BaseBackendConfig,
    ChromaDBConfig,
    CompressionConfig,
    EmbeddingConfig,
    PostgreSQLConfig,
    QdrantConfig,
    RedisConfig,
    SQLiteConfig,
    create_backend_config,
)

__all__ = [
    "BaseMemoryBackend",
    "BaseBackendConfig",
    "SQLiteConfig",
    "PostgreSQLConfig",
    "RedisConfig",
    "ChromaDBConfig",
    "QdrantConfig",
    "EmbeddingConfig",
    "CompressionConfig",
    "create_backend_config",
]
