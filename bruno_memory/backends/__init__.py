"""
Memory backend implementations for bruno-memory.

Provides concrete implementations of the BaseMemoryBackend
for different storage systems.
"""

from .sqlite import SQLiteMemoryBackend
from .postgresql import PostgreSQLMemoryBackend
from .redis import RedisMemoryBackend
from .vector import ChromaDBBackend, QdrantBackend

# Import and register backends with factory
from ..factory import register_backend
from ..base import SQLiteConfig, PostgreSQLConfig, RedisConfig, ChromaDBConfig, QdrantConfig

# Auto-register backends
register_backend('sqlite', SQLiteMemoryBackend, SQLiteConfig)
register_backend('postgresql', PostgreSQLMemoryBackend, PostgreSQLConfig)
register_backend('redis', RedisMemoryBackend, RedisConfig)
register_backend('chromadb', ChromaDBBackend, ChromaDBConfig)
register_backend('qdrant', QdrantBackend, QdrantConfig)

__all__ = [
    'SQLiteMemoryBackend',
    'PostgreSQLMemoryBackend',
    'RedisMemoryBackend',
    'ChromaDBBackend',
    'QdrantBackend',
]