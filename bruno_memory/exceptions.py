"""
Custom exception hierarchy for bruno-memory.

Defines specific exception types for different error conditions
in the memory management system.
"""


class MemoryError(Exception):
    """Base exception for all bruno-memory related errors."""
    pass


class BackendNotFoundError(MemoryError):
    """Raised when a requested backend is not available or registered."""
    pass


class ConfigurationError(MemoryError):
    """Raised when there's an invalid configuration."""
    pass


class ConnectionError(MemoryError):
    """Raised when connection to storage backend fails."""
    pass


class ValidationError(MemoryError):
    """Raised when data validation fails."""
    pass


class OperationError(MemoryError):
    """Raised when a storage operation fails."""
    pass


class MigrationError(MemoryError):
    """Raised when database migration fails."""
    pass


class SerializationError(MemoryError):
    """Raised when serialization/deserialization fails."""
    pass


class CacheError(MemoryError):
    """Raised when cache operations fail."""
    pass


class EmbeddingError(MemoryError):
    """Raised when embedding operations fail."""
    pass


class CompressionError(MemoryError):
    """Raised when memory compression fails."""
    pass


class AuthenticationError(MemoryError):
    """Raised when authentication to backend fails."""
    pass


class PermissionError(MemoryError):
    """Raised when insufficient permissions for operation."""
    pass