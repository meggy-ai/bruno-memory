"""
bruno-memory: Memory storage and retrieval system for Bruno AI Platform

A comprehensive memory management package that implements the bruno-core MemoryInterface
with support for multiple storage backends (SQLite, PostgreSQL, Redis, ChromaDB, Qdrant).
"""

from typing import Optional

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("bruno-memory")
except PackageNotFoundError:
    # Package is not installed, use a fallback version
    __version__ = "0.1.0-dev"

# Import main factory for easy access
from .factory import MemoryFactory
from .exceptions import (
    MemoryError,
    BackendNotFoundError,
    ConfigurationError,
    ConnectionError,
    ValidationError,
    OperationError,
)

__all__ = [
    "__version__",
    "MemoryFactory", 
    "MemoryError",
    "BackendNotFoundError", 
    "ConfigurationError",
    "ConnectionError",
    "ValidationError",
    "OperationError",
]