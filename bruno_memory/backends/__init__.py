"""
Memory backend implementations for bruno-memory.

Provides concrete implementations of the BaseMemoryBackend
for different storage systems.
"""

from .sqlite import SQLiteMemoryBackend
from .postgresql import PostgreSQLMemoryBackend

# Import and register backends with factory
from ..factory import register_backend
from ..base import SQLiteConfig, PostgreSQLConfig

# Auto-register backends
register_backend('sqlite', SQLiteMemoryBackend, SQLiteConfig)
register_backend('postgresql', PostgreSQLMemoryBackend, PostgreSQLConfig)

__all__ = [
    'SQLiteMemoryBackend',
    'PostgreSQLMemoryBackend',
]