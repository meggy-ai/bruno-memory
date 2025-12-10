"""
Memory backend implementations for bruno-memory.

Provides concrete implementations of the BaseMemoryBackend
for different storage systems.
"""

from .sqlite import SQLiteMemoryBackend

# Import and register backends with factory
from ..factory import register_backend
from ..base import SQLiteConfig

# Auto-register SQLite backend
register_backend('sqlite', SQLiteMemoryBackend, SQLiteConfig)

__all__ = [
    'SQLiteMemoryBackend'
]