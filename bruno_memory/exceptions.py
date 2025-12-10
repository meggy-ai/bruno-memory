"""
Custom exceptions for bruno-memory.

This module defines the exception hierarchy for bruno-memory,
extending bruno-core's base exceptions where appropriate.
"""

from typing import Any, Optional


class MemoryError(Exception):
    """Base exception for all bruno-memory errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize memory error.

        Args:
            message: Error message
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of error."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class BackendError(MemoryError):
    """Base exception for backend-related errors."""

    pass


class ConnectionError(BackendError):
    """Failed to connect to storage backend."""

    pass


class DatabaseError(BackendError):
    """Database operation failed."""

    pass


class QueryError(DatabaseError):
    """Database query failed."""

    pass


class TransactionError(DatabaseError):
    """Database transaction failed."""

    pass


class MigrationError(DatabaseError):
    """Database migration failed."""

    pass


class ConfigurationError(MemoryError):
    """Invalid backend configuration."""

    pass


class StorageError(MemoryError):
    """Failed to store data."""

    pass


class RetrievalError(MemoryError):
    """Failed to retrieve data."""

    pass


class SerializationError(MemoryError):
    """Failed to serialize/deserialize data."""

    pass


class CacheError(MemoryError):
    """Cache operation failed."""

    pass


class CompressionError(MemoryError):
    """Failed to compress or summarize memory."""

    pass


class EmbeddingError(MemoryError):
    """Failed to generate or manage embeddings."""

    pass


class SessionError(MemoryError):
    """Session management error."""

    pass


class ContextError(MemoryError):
    """Context building or management error."""

    pass


class ValidationError(MemoryError):
    """Data validation failed."""

    pass


class BackupError(MemoryError):
    """Backup or export operation failed."""

    pass


class ImportError(MemoryError):
    """Import operation failed."""

    pass


class AnalyticsError(MemoryError):
    """Analytics operation failed."""

    pass


# Backend-specific exceptions

class SQLiteError(DatabaseError):
    """SQLite backend error."""

    pass


class PostgreSQLError(DatabaseError):
    """PostgreSQL backend error."""

    pass


class RedisError(BackendError):
    """Redis backend error."""

    pass


class VectorDBError(BackendError):
    """Vector database error."""

    pass


class ChromaDBError(VectorDBError):
    """ChromaDB backend error."""

    pass


class QdrantError(VectorDBError):
    """Qdrant backend error."""

    pass
